#include <LiquidCrystal.h>

#include <LiquidCrystal.h>

#include <DHT.h>
#include <Wire.h>


#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

const int gasPin = A0;
const int ldrPin = A1;
const int led1Pin = A2;
const int led2Pin = A3;
const int fanPin = 5;
const int buzzerPin = 9;

bool buzzerEnabled = false;
bool buzzerOnFromTemp = false;

void setup() {
  Serial.begin(9600);
  dht.begin();
 

  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  digitalWrite(led1Pin, LOW);
  digitalWrite(led2Pin, LOW);
  digitalWrite(fanPin, LOW);
  digitalWrite(buzzerPin, LOW);
}

void loop() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int gas = analogRead(gasPin);
  int ldr = analogRead(ldrPin);

  // Display temperature on LCD
 


  // Serial read
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "READ") {
      Serial.print("{\"temp\":");
      Serial.print(temp);
      Serial.print(",\"hum\":");
      Serial.print(hum);
      Serial.print(",\"gas\":");
      Serial.print(gas);
      Serial.print(",\"ldr\":");
      Serial.print(ldr);
      Serial.println("}");
    }
    else if (cmd == "LED1_ON") digitalWrite(led1Pin, HIGH);
    else if (cmd == "LED1_OFF") digitalWrite(led1Pin, LOW);
    else if (cmd == "LED2_ON") digitalWrite(led2Pin, HIGH);
    else if (cmd == "LED2_OFF") digitalWrite(led2Pin, LOW);
    else if (cmd == "Ac_ON") digitalWrite(fanPin, HIGH);
    else if (cmd == "Ac_OFF") digitalWrite(fanPin, LOW);
    else if (cmd == "BUZZER_ENABLE") buzzerEnabled = true;
    else if (cmd == "BUZZER_DISABLE") {
      buzzerEnabled = false;
      digitalWrite(buzzerPin, LOW);
    }
    else if (cmd == "BUZZER_ON" && buzzerEnabled) digitalWrite(buzzerPin, HIGH);
    else if (cmd == "BUZZER_OFF") digitalWrite(buzzerPin, LOW);
    else if (cmd == "BUZZER_TEST") {
      digitalWrite(buzzerPin, HIGH);
      delay(1000);
      digitalWrite(buzzerPin, LOW);
    }
  }

  // Auto-buzzer logic if temp < 26
  if (buzzerEnabled && temp < 30 && !buzzerOnFromTemp) {
    digitalWrite(buzzerPin, HIGH);
    buzzerOnFromTemp = true;
  }
  else if ((temp >= 30 || !buzzerEnabled) && buzzerOnFromTemp) {
    digitalWrite(buzzerPin, LOW);
    buzzerOnFromTemp = false;
  }

  delay(1000);
}
