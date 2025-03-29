from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import cv2
import dlib
import numpy as np
import uvicorn
from PIL import Image
from io import BytesIO
from twilio.rest import Client
from temp_DB import create_connection
from dotenv import load_dotenv 
import os 
app = FastAPI()

load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")


client = Client(account_sid, auth_token)




templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')


def get_face_embedding(image, detector, predictor, face_rec_model):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_image)
    
    if len(faces) == 0:
        return None  
    
    face = faces[0]
    landmarks = predictor(gray_image, face)
    face_embedding = face_rec_model.compute_face_descriptor(image, landmarks)
    return np.array(face_embedding)


def compare_embeddings(embedding1, embedding2, threshold=0.4):
    distance = np.linalg.norm(embedding1 - embedding2)
    return distance < threshold 




def fetch_and_display_images():
    """Fetch and display all images from the confidential table."""

    collector = []
    conn, cursor = create_connection()
    if conn is None:
        return []  # Return empty list if DB connection fails
    
    try:
        cursor.execute("SELECT ID, name, data, Img FROM confidential;")
        rows = cursor.fetchall()
        for row in rows:
            cartoon_id, name, data, cartoon_img = row
            print(cartoon_id,name,data)
            if cartoon_img:
                image = Image.open(BytesIO(cartoon_img))
                
                collector.append(np.array(image)) 
    except Exception as error:
        print("Error fetching images:", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
    return collector


video_capture = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg",frame)  
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")




images=fetch_and_display_images()

# create embeddings for all images in the folder
embeddings_folder = []
for img in images:
    embedding = get_face_embedding(img, detector, predictor, face_rec_model)
   
    if embedding is not None:
        embeddings_folder.append(embedding)
    else:
        embeddings_folder.append(None)


@app.post("/capture", response_class=HTMLResponse)
async def capture_image(request: Request):
    success, frame = video_capture.read()
    if success:
        captured_image = frame
        captured_embedding = get_face_embedding(captured_image, detector, predictor, face_rec_model)
        
        if captured_embedding is None:
            return templates.TemplateResponse("home.html", {"request": request, "no_face":True})
        
        match_found = False
        matched_image_path = None
        
        for i, embedding in enumerate(embeddings_folder):
            if embedding is not None and compare_embeddings(captured_embedding, embedding):
                conn, cursor = create_connection()
                query = "SELECT name, data FROM confidential WHERE ID = %s;"
                cursor.execute(query, (i+1,))
                result = cursor.fetchone()
               
                matched_image = images[i]
               
                matched_image_path = "static/match_image.jpg"
                matched_image_rgb = cv2.cvtColor(matched_image, cv2.COLOR_BGR2RGB)
                cv2.imwrite(matched_image_path, matched_image_rgb)
                match_found = True
                break

        # save the captured image
        captured_image_path = "static/captured_image.jpg"
        cv2.imwrite(captured_image_path, frame)

        if match_found:
            message = client.messages.create(
                        body='Threat detected',  # SMS content
                        from_= os.getenv("TWILIO_NUMBER"),  # Twilio number
                        to=os.getenv("REC")      # Recipient's phone number
                        )


            print(f"Message sent with SID: {message.sid}")
            
            return templates.TemplateResponse("home.html", {
                "request": request,
                "message": "Image captured successfully!",
                "captured_path": captured_image_path,
                "matched_path": matched_image_path,
                "name":result[0],
                "data":result[1],
            })
            
        else:
            return templates.TemplateResponse("home.html", {
                "request": request,
                "message": "No match found.",
                "captured_path": captured_image_path,
                "matched_path": None,
            })
    else:
        return templates.TemplateResponse("home.html", {"request": request, "message": "Failed to capture image."})
    
if __name__=="__main__":
    uvicorn.run(app=app,host="0.0.0.0",port=8000)