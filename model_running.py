from ultralytics import YOLO
import cv2

# load trained YOLO model weights

model = YOLO("runs/detect/train/weights/best.pt")

# open the webcam (use 0 for the default webcam)

cap = cv2.VideoCapture(0)

while True:
   
    ret, frame = cap.read()
    if not ret:
        break

    
    results = model(frame,conf=0.6)

   
    frame_with_detections = results[0].plot()

  
    cv2.imshow("Webcam Feed", frame_with_detections)

    # break the loop if 'q' is pressed
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
