import cv2
import torch
from yolov7_script import detect

# Device selection
device = 'cpu'

# Load YOLOv7 model
weights_path = r"C:\Users\Admin\PycharmProjects\YOLOV7\yolov7_train\yolov7\pretrain\yolov7.pt"
img_size = 640
iou_thres = 0.45
conf_thres = 0.91

# URL for the Android camera video stream
url="http://192.168.1.194:8080/video"


video = cv2.VideoCapture(url)

# While loop to continuously fetching data from the URL
while True:
    flag, frame = video.read()
    # Perform object detection using YOLOv7
    with torch.no_grad():
        detect_result = detect(source=url, weights=weights_path, device=device, img_size=img_size,
                               iou_thres=iou_thres, conf_thres=conf_thres)

    # Check if "fire" class is detected with confidence > 60%
    for result in detect_result:
        if result['label'] == 'Fire 🔥' and result['confidence'] > 0.60:
            print("Fire detected!")

    cv2.imshow("Android_cam", frame)

    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        break

# Release video capture and close all windows
video.release()
cv2.destroyAllWindows()
