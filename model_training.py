from ultralytics import YOLO

# load a pre-trained YOLO model (you can choose n, s, m, l, or x versions)

model = YOLO("yolo11n.pt")

# training on your custom dataset

model.train(data="custom_dataset.yaml", epochs=100)