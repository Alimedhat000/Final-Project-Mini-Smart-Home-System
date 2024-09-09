# Face Detection and Recognition System

This project utilizes **YuNet** for face detection and **DeepFace** for face recognition. It captures faces from a webcam feed, saves the detected face to a local folder, and compares it against a database of known faces using DeepFace.

## Overview

This application uses OpenCV's **YuNet face detection** model and **DeepFace** for face recognition. It performs real-time face detection via a webcam, captures detected faces, and compares them with images stored in a local database. If a face match is found, it will display the name of the person; otherwise, it will mark the face as "Unknown."

## Requirements

- Python 3.x
- OpenCV
- DeepFace
- ONNX runtime for face detection with YuNet
- A webcam for capturing images

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/your-username/face-recognition-system.git
    cd face-recognition-system
    ```

2. Install the required dependencies:

    ```bash
    pip install opencv-python-headless deepface onnxruntime
    ```

3. Download the YuNet ONNX face detection model from [YuNet ONNX](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet).

4. Prepare your face recognition database by adding images in a folder. Ensure each image file is named with a person's name as a prefix (e.g., `John_Doe_1.jpg`).

## Usage

1. Modify the database path (`db_path`) in the script to point to your image folder.

2. Run the script:

    ```bash
    python face_detection_recognition.py
    ```

3. Press `q` to exit the application.

## How it Works

- The system uses **YuNet** (an ONNX-based face detection model) to detect faces in real-time from a webcam feed.
- Detected faces are saved locally and then passed to **DeepFace** for recognition.
- **DeepFace** compares the captured face against a database of pre-saved images using the **Facenet** model.
- The system will annotate the frame with either the recognized person's name or "Unknown."

### Key Components

- **YuNet for Face Detection**: YuNet is an ONNX-based face detector model that is lightweight and efficient, making it suitable for real-time detection.
- **DeepFace for Face Recognition with Facenet model**: DeepFace provides a powerful face recognition framework and in this project, it uses the Facenet model for recognizing faces.

## Conclusion from faceDetection.ipynb

The `faceDetection.ipynb` notebook demonstrates the effectiveness of the face detection and recognition system. The key conclusions are:

- The YuNet model is capable of detecting faces in real-time with high accuracy.
- DeepFace successfully recognizes faces from the database and annotates them correctly.
- The system is efficient and performs well under various lighting conditions and angles.
- The combination of YuNet for detection and DeepFace for recognition with the Facenet model provides a robust solution for real-time face recognition applications.