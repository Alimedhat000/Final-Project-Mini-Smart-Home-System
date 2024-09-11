#ifndef SMART_HOME_SYSTEM_H
#define SMART_HOME_SYSTEM_H

#include <Arduino.h>
#include <Servo.h>

// ForceOpen
extern bool ForceOpen;

// FaceDetection
extern bool FaceDetected;

// Password Lock
extern char Cur_Pass[15];
extern char Entered_Pass[15];
extern short Entered_index;
extern bool CorrectPass;
extern bool PressedEnter;

// Motor driver pins
#define MOTOR_DRIVER_INPUT1 PIN_PD2
#define MOTOR_DRIVER_INPUT2 PIN_PD4
#define MOTOR_DRIVER_ENABLE PIN_PB3

// Servo configuration
#define SERVO_PIN PIN_PB1

// Sensors
#define LDR_PIN PIN_PC2
#define THERMISTOR_PIN PIN_PC3
#define THERMISTOR_NOMINAL 10000.0
#define TEMPERATURE_NOMINAL 25.0
#define BCOEFFICIENT 3380
#define SERIES_RESISTOR 10000.0

// Keypad
#define KEYPAD_PIN PIN_PC0

// LEDs
#define TEST_LED PIN_PB0
#define RED_LED PIN_PD5
#define GREEN_LED PIN_PD6
#define BLUE_LED PIN_PD7

// PIR sensor
#define PIR_PIN PIN_PC4

// Buzzer
#define BUZZER_PIN PIN_PD3

// Function declarations
void InitializePins();
void HandleSerialInput();
void HandleKeypadInput(char key);
void CheckPassword();
void ChangePassword(const char* newPassword);
void OpenDoor();
void CLoseDoor();
char GetKeyValue();
int GetTemp();
void LightGreen();
void LightBlue();
void LightRed();
void DisplayTempOnRGB(float temperature);
void BeepBuzzer();
void StartFan();
void SetFanSpeed(int value);
void ControlFanSpeed(float temperature);
void DetectMotion();
void ControlLight();

#endif  // SMART_HOME_SYSTEM_H
