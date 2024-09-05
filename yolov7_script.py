from pathlib import Path
import cv2
import torch
import time
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

from Adafruit_IO import MQTTClient
import base64

import fbchat
import json

# Adafruit io connecting
AIO_USERNAME = "your_username"
AIO_KEY = "your_aio_key"

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.connect()
client.loop_background()
# Disable scientific notation for clarity
# np.set_printoptions(suppress=True)

#Facebook connecting
with open(r"C:\Users\Admin\PycharmProjects\YOLOV7\fb_cookies.json") as f:
    cookies = json.load(f)
username = "username"
password = "password"
maxxx = fbchat.Client(username, password,session_cookies=cookies)

name = "friend name"
friends = maxxx.searchForUsers(name) # return a list of names
friend = friends[0] #Modify if you want to send to more people


def detect(source, weights, device, img_size, iou_thres, conf_thres):
    fire_detected_flag = False

    # Initialize
    set_logging()
    device = select_device(device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(img_size, s=stride)  # check img_size


    # Set Dataloader

    cudnn.benchmark = True  # set True to speed up constant image size inference
    dataset = LoadStreams(source, img_size=imgsz, stride=stride)


    # get name and color
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # run inference
    if device.type != 'cpu':
        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))
    old_img_w = old_img_h = img_size
    old_img_b = 1

    t0 = time.perf_counter()

    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()
        img /= 255.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        if device.type != 'cpu' and (
                old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]

        # inference

        with torch.no_grad():
            pred = model(img)[0]


        pred = non_max_suppression(pred, conf_thres, iou_thres)

        for i, det in enumerate(pred):
            p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            p = Path(p)

            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
            if len(det):
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)},"

                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]}{conf:.2f}'
                    confident_scoress = float(conf) * 100
                    client.publish("confident_score", confident_scoress )
                    if names[int(cls)] == 'Fire' and float(conf) > 0.60 and not fire_detected_flag:
                        msg = "Fire detected!"
                        client.publish("class", msg)
                        sent = maxxx.sendMessage(msg, thread_id=friend.uid)
                        if sent:
                            print("Message sent successfully!")
                        fire_detected_flag = True

                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=1)
        cv2.imshow(str(p), im0)
        # Convert the image to JPEG format
        im0_reshaped = cv2.resize(im0, (224, 224), interpolation=cv2.INTER_AREA)
        img_encoded = cv2.imencode('.jpg', im0_reshaped)[1]

        # Encode the JPEG image as base64
        encoded_data = base64.b64encode(img_encoded).decode('utf-8')
        client.publish("ai", encoded_data)
        time.sleep(1)
 
        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break
    print(f"Done, ({time.perf_counter() - t0:.3f}s)")

# Device selection
device = 'cpu'

# Load YOLOv7 model
weights_path = "best.pt"
img_size = 640
iou_thres = 0.1
conf_thres = 0.45

# URL for the Android camera video stream (using IP Webcam app)
url = "http://____:8080/video" 

# While loop to continuously fetching data from the URL
while True:
    detect_results = detect(source=url, weights=weights_path, device=device, img_size=img_size,
                                    iou_thres=iou_thres, conf_thres=conf_thres)
