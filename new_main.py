import cv2
from yolov7_script import detect

# Device selection
device = 'cpu'

# Load YOLOv7 model
weights_path = r"C:\Users\Admin\PycharmProjects\YOLOV7\yolov7_train\yolov7\pretrain\yolov7.pt"
img_size = 640
iou_thres = 0.45
conf_thres = 0.91

# URL for the Android camera video stream
url = "http://172.16.131.106:8080/video"

# While loop to continuously fetching data from the URL
while True:
    detect_results = detect(source=url, weights=weights_path, device=device, img_size=img_size,
                                    iou_thres=iou_thres, conf_thres=conf_thres)



