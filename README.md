# Mini Smart Home System

## Overview
This project is a comprehensive **Mini Smart Home System** integrating **face recognition** and **ATmega8A** microcontroller, featuring multiple sensors, motors, and a custom PCB design. The system allows for automated door access, temperature control, lighting management, and security alerts, offering a fully functional smart home environment.

## Features
- **Face Recognition**: Real-time facial detection and recognition using OpenCV and DeepFace.
- **Hand Recognition**: Real-time hand gestures detection to open the door and deteremine the livelessness of the user using mediapipe.
- **Password Verification**: Secure door access using a keypad-based password system.
- **Sensors Integration**:
  - Temperature sensor for environment monitoring.
  - Motion detection for security alerts.
  - Light sensor to adjust home lighting.
- **Motor and Servo Control**: Automates door locking/unlocking and fan control.
- **Alarm System**: Alerts triggered by incorrect password entries.
- **User Interface**: GUI developed in Python (Tkinter) for controlling the system and monitoring home conditions.
- **Custom PCB Design**: Designed using Altium Designer for interfacing the sensors, motors, and microcontroller.

## System Architecture
The system is composed of two main components:
1. **Software**:
   - **Face Recognition**: Python-based system using OpenCV and DeepFace.
   - **GUI Interface**: Allows interaction with the system, displaying alerts and controlling components.
   - **Serial Communication**: Facilitates communication between the PC and ATmega8A using Pyserial for sending and receiving commands.
   
2. **Hardware**:
   - **ATmega8A Microcontroller**: Controls the sensors, motors, and LEDs.
   - **Custom PCB**: Interfaces the microcontroller with sensors and actuators.
   - **Sensors**: Includes temperature, motion, and light sensors.
   - **Motors**: Servo motor for door control and DC motors for fans.

## Project Setup

### Prerequisites
- **Hardware**:
  - ATmega8A Microcontroller
  - 16MHz Crystal and 22pf Capacitors 
  - Sensors: Temperature, Motion, Light
  - Servo Motor, DC Motor
  - Keypad for password input
  - Buzzer for alerts
  
- **Software**:
  - Python 3.x
  - Pyserial
  - OpenCV, TensorFlow, DeepFace, Mediapipe
  - Tkinter (GUI)
  - Arduino IDE (for ATmega8A programming)

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/mini-smart-home-system.git
   cd Final Project Mini Smart Home System
   ```
2. **Install Required Python Packages**:
  ```bash
   pip install opencv-python tensorflow deepface pillow pyserial mediapipe numpy
  ```
3. **Upload Firmware and BootLoader to Atmega8A**:
  - use Arduino IDE to flash the bootloader using Arduino as ISP while choosing the correct clock and baudrate.
  - Flash the code using the programmer 
4. **Connect the Hardware to COM4 and Power It**

5. **Run the System**:
  ```bash
python GUI/GUI&Hand_detector.py
```
### PCB Design 
 - The PCB was designed using Altium Designer. The design , the liberaries made for each component 
 and all other files can be found in the `PcbDesign/` directory.

### Acknowledgements
Special thanks to **MindCloud Team**, our **FaceRecognition Team** **Rowan** and **Ebraim**, the **ATMEGA8a** team **ALi** and **Ahmed** , and our **PCB designer** **Menna** 

