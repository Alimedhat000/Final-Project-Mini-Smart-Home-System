#include "HardwareSerial.h"
#include <Servo.h>
#include "Defines.h"

char Cur_Pass[15] = "1234";  // Default password
char Entered_Pass[15] = "";  // Adjust size as needed
short Entered_index = 0;
bool CorrectPass = false;
bool PressedEnter = false;
bool ForceOpen = false;
bool FaceDetected = false;

Servo Door;

void InitializePins() {
  pinMode(MOTOR_DRIVER_INPUT1, OUTPUT);
  pinMode(MOTOR_DRIVER_INPUT2, OUTPUT);
  pinMode(MOTOR_DRIVER_ENABLE, OUTPUT);
  pinMode(KEYPAD_PIN, INPUT);
  pinMode(TEST_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(TEST_LED, LOW);
  Door.attach(SERVO_PIN);
}

void HandleSerialInput() {
  if (Serial.available()) {
    char command[20];  // Adjust size as needed
    int length = Serial.readBytesUntil('\n', command, sizeof(command) - 1);
    command[length] = '\0';  // Null-terminate string

    if (strncmp(command, "CHANGE_PASS:", 12) == 0) {
      ChangePassword(command + 12);
    } else if (strcmp(command, "OPEN_DOOR") == 0) {
      OpenDoor();
    } else if (strcmp(command, "FACE_DETECTED") == 0) {
      FaceDetected = true;
    } else if (strcmp(command, "FORCE_OPEN") == 0) {
      ForceOpen = true;
    } else if (strcmp(command, "SHOW_PASS") == 0) {
      Serial.println(Cur_Pass);
    }
  }
}

void HandleKeypadInput(char key) {
  if (key == '#') {  // Enter Key
    CheckPassword();
    Serial.println();
  } else if (Entered_index < 15) {
    Serial.print(key);
    Entered_index++;
    strncat(Entered_Pass, &key, 1);
  } else {
    Serial.println(F("Password length exceeded!"));
    BeepBuzzer();       // Sound the buzzer or indicate an error
    Entered_Pass[0] = '\0';  // Clear the entered password
    Entered_index = 0;
  }
}

void ChangePassword(const char* new_Pass) {
  strncpy(Cur_Pass, new_Pass, sizeof(Cur_Pass) - 1);
  Cur_Pass[sizeof(Cur_Pass) - 1] = '\0';  // Null-terminate
  Serial.println(F("Password Changed Successfully."));
  Entered_Pass[0] = '\0';  // Clear the entered password
  CorrectPass = false;
}

void CheckPassword() {
  PressedEnter = true;
  if (strcmp(Cur_Pass, Entered_Pass) == 0) {
    Serial.println(F("Password Correct. Opening Door."));
    CorrectPass = true;
  } else {
    Serial.println(F("Incorrect Password."));
  }
  Entered_Pass[0] = '\0';  // Clear the entered password
}

void OpenDoor() {
  Door.write(90);
}
void CLoseDoor() {
  Door.write(0);
}

char GetKeyValue() {
  // int reading = 0;
  // for (int i = 0; i < 5; i++) {
  //   reading += analogRead(KEYPAD_PIN);
  //   delay(5);  // Reduced delay for better responsiveness
  // }
  int averageADC = analogRead(KEYPAD_PIN);

  static int lastADC = -1;
  static unsigned long lastReadTime = 0;
  unsigned long currentTime = millis();

  if (abs(averageADC - lastADC) > 20 || currentTime - lastReadTime > 150) {
    lastADC = averageADC;
    lastReadTime = currentTime;

    // Simplified mapping
    if (averageADC <= 30) return '1';
    if (averageADC <= 99) return '2';
    if (averageADC <= 170) return '3';
    if (averageADC <= 230) return 'A';
    if (averageADC <= 320) return '4';
    if (averageADC <= 350) return '5';
    if (averageADC <= 400) return '6';
    if (averageADC <= 430) return 'B';
    if (averageADC <= 490) return '7';
    if (averageADC <= 520) return '8';
    if (averageADC <= 545) return '9';
    if (averageADC <= 575) return 'C';
    if (averageADC <= 604) return '*';
    if (averageADC <= 624) return '0';
    if (averageADC <= 644) return '#';
    if (averageADC <= 660) return 'D';

    return 0;
  }
  return 0;
}

int GetTemp() {
  int reading = 0;
  for (int i = 0; i < 5; i++) {
    reading += analogRead(THERMISTOR_PIN);
    delay(10);
  }
  int analogValue = reading / 5;

  if (analogValue == 0) return -1;

  float resistance = SERIES_RESISTOR / (1023.0 / analogValue - 1.0);
  float temperature = resistance / THERMISTOR_NOMINAL;
  temperature = log(temperature);
  temperature /= BCOEFFICIENT;
  temperature += 1.0 / (TEMPERATURE_NOMINAL + 273.15);
  temperature = 1.0 / temperature;
  temperature -= 273.15;

  return temperature;
}

void LightGreen() {
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BLUE_LED, LOW);
}

void LightBlue() {
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BLUE_LED, HIGH);
}

void LightRed() {
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, HIGH);
  digitalWrite(BLUE_LED, LOW);
}

void DisplayTempOnRGB(float temperature) {
  Serial.print("TEMP :");
  Serial.print(temperature);
  if (temperature > 30) {
    LightRed();
  } else if (temperature > 20) {
    LightGreen();
  } else {
    LightBlue();
  }
}

void BeepBuzzer() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(500);
  digitalWrite(BUZZER_PIN, LOW);
}

void SetFanSpeed(int value) {
  analogWrite(MOTOR_DRIVER_ENABLE, value);
}

void ControlFanSpeed(float temperature) {
  int speed;
  if (temperature > 30) {
    speed = 255;  // Max speed
  } else if (temperature > 20) {
    speed = map(temperature, 20, 30, 128, 255);
  } else {
    speed = 128;
  }
  SetFanSpeed(speed);
}

void DetectMotion() {
  if (digitalRead(PIR_PIN)) {
    Serial.println(F("Motion detected: Someone is inside."));
    digitalWrite(TEST_LED, HIGH);
    delay(1000);
    digitalWrite(TEST_LED, LOW);
  }
}

void ControlLight() {
  int lightLevel = analogRead(LDR_PIN);
  Serial.print(F("LIGHT LEVEL: "));
  Serial.println(lightLevel);
  int brightness = map(lightLevel, 0, 1023, 255, 0);
  analogWrite(TEST_LED, brightness);
}
