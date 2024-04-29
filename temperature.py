import sys
from Adafruit_IO import MQTTClient
import random as r
import time
import requests
import warnings
from account import AIO_USERNAME, AIO_KEY

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def connected(client):
    print("Connected")
def disconnected(client):
    print("Disconnecting...")
    sys.exit(1)

client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected

client.connect()
client.loop_background()

if __name__ == '__main__':
    while True:
        temp_value = r.randint(25, 42)
        time.sleep(2)
        client.publish("temperature", temp_value)
