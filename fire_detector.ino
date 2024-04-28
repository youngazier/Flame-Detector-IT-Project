#include <ESP8266WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

#define fireSensor D0
#define redPin D4
#define greenPin D5
#define buzzer D6

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

void MQTT_connect();

void notifyOnFire() {
}

void setup() {
  Serial.begin(115200);
  pinMode(fireSensor, INPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
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
    Serial.print(".");
  }
  // digitalWrite(redPin, LOW);
  // digitalWrite(greenPin, HIGH);
  // Serial.println();

  Serial.println("Wifi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  MQTT_connect();

  Fire_detected = digitalRead(fireSensor);
  Serial.println(Fire_detected);

  if (Fire_detected == LOW) {
    Serial.println("Fire Detected!");
    FireDetector.publish(0);
    digitalWrite(greenPin, LOW);
    digitalWrite(redPin, HIGH);
    // playMelody();
    tone(buzzer, 1000);
    delay(1000);
    // delay(500);
    // digitalWrite(buzzer, LOW);
    // digitalWrite(redPin, LOW);
  } else {
    Serial.println("Safe");
    FireDetector.publish(1);
    digitalWrite(redPin, LOW);
    digitalWrite(greenPin, HIGH);
    noTone(buzzer);
    delay(5000);
    // digitalWrite(greenPin, LOW);
  }

//   if (!FireDetector.publish(Fire_detected)) {
//     Serial.println(F("Fire Detector Failed"));
//   } else {
//     Serial.println(F("Fire Detector OK!"));
//   }
//   delay(100);
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

// void playMelody()
// {
//   // Play a simple melody: C4, E4, G4, C5
//   tone(buzzer, 262, 200);             // C4
//   delay(200);
//   tone(buzzer, 330, 200);             // E4
//   delay(200);
//   tone(buzzer, 392, 200);             // G4
//   delay(200);
//   tone(buzzer, 523, 200);             // C5
//   delay(200);
// }
