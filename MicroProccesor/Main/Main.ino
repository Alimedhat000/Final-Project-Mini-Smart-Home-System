#include "Defines.h"

Servo Door;
unsigned long correctPassTime = 0;  // Time when the correct password was entered
bool systemResetRequired = false;   // Flag to indicate if reset is needed
static unsigned long lastReadTime = 0;
static unsigned long lastSenseTime = 0;
unsigned long currentTime = millis();

void setup() {
  Door.attach(SERVO_PIN);
  InitializePins();
  StartFan();
  Serial.begin(19200);
}
void loop() {
  currentTime = millis();
  int temperature = GetTemp();
  HandleSerialInput();

  // Get keypad input every 150ms
  if (currentTime - lastReadTime > 220) {
    lastReadTime = currentTime;
    char key = GetKeyValue();
    if (key) {
      HandleKeypadInput(key);
    }
  }

  // Handle correct password entry
  if (PressedEnter) {
    if (CorrectPass) {
      // Reset the 10-second window each time the correct password is entered
      correctPassTime = millis();
      systemResetRequired = true;

      // Actions to perform after the correct password entry
      DetectMotion();
      OpenDoor();
      ControlLight();
      DisplayTempOnRGB(temperature);
      ControlFanSpeed(temperature);

      // Reset `PressedEnter` only after performing actions
      PressedEnter = false;
      CorrectPass = false;  // Allow for the next password check
    } else {
      // Incorrect password handling
      Serial.println(F("WARNING! WRONG PASSWORD ENTERED!"));
      BeepBuzzer();
      PressedEnter = false;  // Reset after handling incorrect password
    }
  }

  // Handle face detection or forced opening
  if ((FaceDetected || ForceOpen)) {
    DetectMotion();
    OpenDoor();
    ControlLight();
    DisplayTempOnRGB(temperature);
    ControlFanSpeed(temperature);

    // Reset flags after handling face detection or force open
    FaceDetected = false;
    ForceOpen = false;

    correctPassTime = millis();
    systemResetRequired = true;
  }

  // Check if system reset is required after 10 seconds
  if (systemResetRequired) {
    // Keep reading and controlling sensors for the full 10 seconds

    if (millis() - lastSenseTime > 600) {
      lastSenseTime = millis();
      DetectMotion();
      DisplayTempOnRGB(temperature);
      ControlFanSpeed(temperature);
      ControlLight();
    }


    // Reset the system after 10 seconds of inactivity (since the last correct password entry)
    if (millis() - correctPassTime >= 10000) {
      CLoseDoor();
      SetFanSpeed(0);               // Stop the fan
      digitalWrite(TEST_LED, LOW);  // Reset LED or other indicators
      digitalWrite(RED_LED, LOW);
      digitalWrite(BLUE_LED, LOW);
      digitalWrite(GREEN_LED, LOW);
      correctPassTime = 0;
      // Reset all necessary flags and variables
      systemResetRequired = false;
    }
  }
}
