#include "Defines.h"

unsigned long correctPassTime = 0;  // Time when the correct password was entered
bool systemResetRequired = false;   // Flag to indicate if reset is needed

void setup() {
  InitializePins();
  Serial.begin(9600);
}

void loop() {
  int temperature = GetTemp();
  HandleSerialInput();
  char key = GetKeyValue();
  if (key) {
    HandleKeypadInput(key);
  }
  if (PressedEnter) {
    if (CorrectPass) {
      if (!systemResetRequired) {
        correctPassTime = millis();
        systemResetRequired = true;
      }
      OpenDoor();
      ControlLight();
      DisplayTempOnRGB(temperature);
      // ControlFanSpeed(temperature);
    } else {
      BeepBuzzer();
      Serial.println(F("WARNING! WRONG PASSWORD ENTERED!"));
      PressedEnter = false;  // Reset after processing
      CorrectPass = false;
    }
  }
  if (FaceDetected || ForceOpen) {
    OpenDoor();
    ControlLight();
    DisplayTempOnRGB(temperature);
    // ControlFanSpeed(temperature);
    if (FaceDetected) {
      FaceDetected = false;  // Reset after processing
    }
    if (ForceOpen) {
      ForceOpen = false;  // Reset after processing
    }
  }
  if (systemResetRequired && (millis() - correctPassTime >= 10000)) {
    // Perform system reset
    CLoseDoor();
    digitalWrite(TEST_LED, LOW);
    PressedEnter = false;
    CorrectPass = false;
    systemResetRequired = false;
  }
}
