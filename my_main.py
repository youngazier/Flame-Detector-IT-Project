import requests
import cv2
import numpy as np
import imutils
import torch
from pathlib import Path
from fbchat import Client
from fbchat.models import *

# Import detect function from your YOLOv7 script
from yolov7_script import detect

# Replace the below URL with your own. Make sure to add "/shot.jpg" at last.
url = "http://192.168.0.103:8080/shot.jpg"

# Device selection
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load YOLOv7 model
weights_path = r"C:\Users\Admin\PycharmProjects\YOLOV7\yolov7_train\yolov7\runs\train\exp\weights\best.pt"
img_size = 640
iou_thres = 0.45
conf_thres = 0.91

# Facebook Messenger credentials
email = 'your_facebook_email'
password = 'your_facebook_password'


# Subclass the Client class
class MessengerClient(Client):
    def send_message_to_user(self, message, user_id):
        self.send(Message(text=message), thread_id=user_id, thread_type=ThreadType.USER)


# While loop to continuously fetching data from the Url
while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    img = imutils.resize(img, width=1000, height=1800)

    # Perform object detection using YOLOv7
    detect_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    detect_image = np.ascontiguousarray(detect_image)

    # Call the detect function
    with torch.no_grad():
        detect_result = detect(source=detect_image, weights=weights_path, device=device, img_size=img_size,
                               iou_thres=iou_thres, conf_thres=conf_thres)

    # Check if "fire" class is detected with confidence > 25%
    for result in detect_result:
        if result['class'] == 'fire' and result['confidence'] > 0.25:
            # Initialize Messenger client
            client = MessengerClient(email, password)
            client.send_message_to_user("Fire detected!", "recipient_user_id")
            client.logout()

    cv2.imshow("Android_cam", img)

    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()