#include <ESP8266WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

#define fireSensor D0
#define redPin D4
#define greenPin D5
#define buzzer D6
#define yellowPin D1

int Fire_detected = HIGH;

// Adafruit IO
#define WLAN_SSID ""
#define WLAN_PASS ""
#define AIO_SERVER "io.adafruit.com"
#define AIO_SERVERPORT 1883
#define AIO_USERNAME ""
#define AIO_KEY ""

//Set up feeds
// AdafruitIO_Feed *fire-sensor = io.feed("fire-sensor");
// AdafruitIO_Feed *temperature = io.feed("temperature");

// MQTT Client
WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);
Adafruit_MQTT_Publish FireDetector = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/fire-sensor");
Adafruit_MQTT_Publish message = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/message");
Adafruit_MQTT_Publish temperature = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/temperature");
Adafruit_MQTT_Subscribe light = Adafruit_MQTT_Subscribe(&mqtt, AIO_USERNAME "/feeds/light");

void MQTT_connect();

void setup() {
  Serial.begin(115200);
  pinMode(fireSensor, INPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(buzzer, OUTPUT);

  // timer.setInterval(1000L, notifyOnFire);

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WLAN_SSID);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(redPin, HIGH);
    delay(500);
    Serial.println("Connecting wifi...");
    Serial.print(".");
  }

  Serial.println("Wifi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  mqtt.subscribe(&light);
}

void loop() {
  MQTT_connect();
  
  //Room Light
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(5000))) {
    if (subscription == &light) {
      Serial.print(F("Got: "));
      String lightstatus = (char *)light.lastread;
      if (lightstatus == "ON")
      {
        digitalWrite(yellowPin, HIGH);
        Serial.println(lightstatus);
      }
      else if (lightstatus == "OFF")
      {
        digitalWrite(yellowPin, LOW);
        Serial.println(lightstatus);
      }
    }
  }

  //Fire sensor
  Fire_detected = digitalRead(fireSensor);
  Serial.println(Fire_detected);

  if (Fire_detected == LOW) {
    Serial.println("Fire Detected!");
    FireDetector.publish(0);
    message.publish("Fire Detected!!!");
    digitalWrite(greenPin, LOW);
    digitalWrite(redPin, HIGH);
    // playMelody();
    tone(buzzer, 1000);
    delay(1000);
  } else {
    Serial.println("Safe");
    FireDetector.publish(1);
    message.publish("Safe");
    digitalWrite(redPin, LOW);
    digitalWrite(greenPin, HIGH);
    noTone(buzzer);
    delay(60000);
  }

  //Random Temperature
  int randNumber = random(20,50);
  temperature.publish(randNumber);
  delay(60000);
}

//Function to connect and reconnect to the MQTT Server.
void MQTT_connect() {
  int8_t ret;

  //Stop if already connected
  if (mqtt.connected()) {
    return;
  }

  Serial.print("Connecting to MQTT ...");
  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) {
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    delay(5000);
    retries--;
    if (retries == 0) {
      //basically die and wait for WDT to reset me
      while (1)
        ;
    }
  }

  Serial.println("MQTT Connected!");
}


