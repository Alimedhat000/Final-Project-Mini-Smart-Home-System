import cv2
import os
import logging

# Suppress TensorFlow logs and warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf

# Suppress TensorFlow warnings related to deprecation
logging.getLogger('tensorflow').setLevel(logging.ERROR)
tf.get_logger().setLevel('ERROR')

from deepface import DeepFace
import tkinter as tk
from tkinter import simpledialog, messagebox, Listbox, Scrollbar, Toplevel
from PIL import Image, ImageTk
import time
import serial
from pathlib import Path
import mediapipe as mp              
import numpy as np

# set path of the database and temporary image
db_path = (Path(__file__).resolve().parent / 'Images').as_posix()
temp_image_path = (Path(__file__).resolve().parent / 'detected_face.jpg').as_posix()


#function to calculate angle between 3 points of the finger 
def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    return angle

# function for Detecting if the hand is closed based on angles
def hand_closed(landmarks_list):
    if(get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8])< 50 and
    get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) < 50 ):
        return  True


# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize face detector using ONNX model
detector = cv2.FaceDetectorYN.create(
    model=(Path(__file__).resolve().parent / 'face_detection_yunet_2023mar.onnx').as_posix(),
    config='',
    input_size=(640, 480),
    score_threshold=0.5,
    nms_threshold=0.4
)

#Initialize the hand detector using MediaPipe
hand_detector = mp.solutions.hands.Hands(
    max_num_hands = 1,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.7,
    model_complexity = 1
)


# Variables to track the time if unknown face has been detected
unknown_start_time = None
unknown_detected = False
last_recognized_face = None      # Track the last recognized face

#variables for drawing hand landmarks
draw_utils = mp.solutions.drawing_utils 
mpHands = mp.solutions.hands


# Initialize serial communication
ser = serial.Serial('COM4', 19200)

def receive_data():
    if ser.in_waiting > 0:
        received_data = ser.read(ser.in_waiting).decode('ascii').rstrip()
        print(f"{received_data}")
       

def add_to_database(name, frame):
    # Detect the face in the frame
    ret, faces = detector.detect(frame)
    if faces is not None and len(faces) > 0:
        for face in faces:
            x, y, w, h = face[0:4].astype(int)
            x, y, w, h = max(0, x), max(0, y), max(1, w), max(1, h)
            out_image = frame[y:y + h, x:x + w]
            cv2.imwrite(temp_image_path, out_image)

            try:
                # Check if the face already exists in the database
                res = DeepFace.find(img_path=temp_image_path, db_path=db_path, enforce_detection=False,
                                    model_name="Facenet")
                if len(res[0]) > 0:
                    #face match is found in the database
                    existing_name = os.path.basename(res[0]['identity'][0]).split("_")[0]
                    messagebox.showerror("Error", f"Face already exists in the database as {existing_name}.")
                    return
            except Exception as e:
                pass

            # If no match is found, add the new face
            img_name = f"{name}.jpeg"
            img_path = os.path.join(db_path, img_name)
            cv2.imwrite(img_path, out_image)
            messagebox.showinfo("Success", f"{name} added to the database.")
    else:
        messagebox.showerror("Error", "No face detected in the frame.")

#function to delete certain images from the database based on given name 
def delete_faces(name):
    img_name = f"{name}.jpeg"
    img_path = os.path.join(db_path, img_name)
    #check if the image exists to delete it
    if os.path.isfile(img_path):
        os.remove(img_path)
        messagebox.showinfo("Success", f"{name}'s image deleted from the database.")
    else:
        messagebox.showerror("Error", f"{name} does not exist in the database.")


#Function to display the dialog for deleting faces
def show_delete_face_dialog():
    # delete face based on the selected name from the list
    def delete_face_from_listbox(event):
        selected_name = listbox.get(listbox.curselection())         
        if selected_name:
            delete_faces(selected_name)                 #calling function to delete the face
            update_face_list()                          #calling function to update the list

    #updating the names on listbox after a face is deleted
    def update_face_list():
        listbox.delete(0, tk.END)                       #clearing the precious listbox
        for filename in os.listdir(db_path):    
            if filename.endswith(".jpeg"):              #If the file is a JPEG image extract the name and add it to the listbox
                listbox.insert(tk.END, filename.split('.')[0])

    #create new window for face deletion dialog
    delete_window = Toplevel(root)      
    delete_window.title("Delete Face")  # Set the title of the new window

    # Create a listbox widget to display names in the database
    listbox = Listbox(delete_window)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)       #fill the window with the list

    # Create a scrollbar for the listbox on the right side of listbox
    scrollbar = Scrollbar(delete_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    #make the listbox scroll using the scrollbar
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    #triggering face deletion when double click is detected
    listbox.bind("<Double-1>", delete_face_from_listbox)
    update_face_list()      #calling function to update the list

# Global flag to check if the dialog is already open 
is_dialog_open = False

def show_add_or_open_dialog():
    global is_dialog_open

    # If a dialog is already open, return and do nothing
    if is_dialog_open:
        return

    is_dialog_open = True  # Set the flag to true to indicate that the dialog is open

    dialog_window = tk.Toplevel()  # Create a new window for the dialog
    dialog_window.title("Unknown Face Detected")
    dialog_window.geometry("300x150")  # Set size for the dialog window

    # Reset the flag when the dialog window is manually closed
    def on_close():
        global is_dialog_open
        is_dialog_open = False
        dialog_window.destroy()

    dialog_window.protocol("WM_DELETE_WINDOW", on_close)  # Bind the close button to reset the flag

    # Label to show the message
    label = tk.Label(dialog_window, text="Unknown face detected.\nDo you want to add it or open the door?")
    label.pack(pady=10)

    # Function to handle adding the face
    def add_face():
        global is_dialog_open
        try:
            name = simpledialog.askstring("Add Face", "Enter name for the new face:")
            if name:
                ret, frame = cap.read()  # Assuming cap is your camera capture object
                if ret:
                    add_to_database(name, frame)  # Add face to the database
                else:
                    messagebox.showerror("Error", "Failed to capture frame.")
        finally:
            is_dialog_open = False  # Reset the flag when the dialog is closed
            dialog_window.destroy()  # Close the dialog after adding

    # Function to handle opening the door
    def open_door():
        global is_dialog_open
        try:
            Open_Door_and_show_window()  # Show the open door window
        finally:
            is_dialog_open = False  # Reset the flag when the dialog is closed
            dialog_window.destroy()  # Close the dialog after opening

    # Function to handle canceling the operation
    def cancel_operation():
        global is_dialog_open
        try:
            messagebox.showinfo("Cancelled", "Operation cancelled.")
        finally:
            is_dialog_open = False  # Reset the flag when the dialog is closed
            dialog_window.destroy()  # Close the dialog after canceling

    # Add button
    add_button = tk.Button(dialog_window, text="Add", command=add_face)
    add_button.pack(side=tk.LEFT, padx=20, pady=20)

    # Open button
    open_button = tk.Button(dialog_window, text="Open", command=open_door)
    open_button.pack(side=tk.LEFT, padx=20, pady=20)

    # Cancel button
    cancel_button = tk.Button(dialog_window, text="Cancel", command=cancel_operation)
    cancel_button.pack(side=tk.LEFT, padx=20, pady=20)

    dialog_window.transient()  # Make the dialog modal (block interaction with the main window)
    dialog_window.grab_set()   # Ensure it captures all events


# Function to display a dialog for changing password
def show_change_password_dialog():
    #saving the new password when save button is clicked
    def save_new_password():
        new_password = password_entry.get()         #enter the password
        if new_password:
            global saved_password
            ser.write(f"CHANGE_PASS:{new_password}".encode())
            saved_password = new_password
            messagebox.showinfo("Success", "Password changed successfully.")
            change_password_window.destroy()  # Close the window after saving
        else:
            messagebox.showerror("Error", "No password entered.")

    global saved_password
    saved_password = ""         #initialize the variable

    # Create a new window for changing the password
    change_password_window = tk.Toplevel(root)
    change_password_window.title("Change Password")

    #label asking the user to enter new password
    tk.Label(change_password_window, text="Enter new password:").pack(padx=20, pady=10)

    #creating entry widget to type the new password with hiding password by *
    password_entry = tk.Entry(change_password_window, show='*')
    password_entry.pack(padx=20, pady=10)

    #creating save password button
    tk.Button(change_password_window, text="Save", command=save_new_password).pack(padx=20, pady=20)

# Function to display notification when the door is opened
def show_open_door_window():
    #creating the window with the title "Open door"
    open_door_window = Toplevel(root)
    open_door_window.title("Open Door")
    #create and place label of the notification
    label = tk.Label(open_door_window, text="Door is now open!")
    label.pack(padx=20, pady=20)
    # Auto-close the window after 5 seconds (5000 milliseconds)
    open_door_window.after(5000, open_door_window.destroy)

def Open_Door_and_show_window():
    show_open_door_window()
    ser.write("FORCE_OPEN".encode())


#function that handles live vid stream with face detection, recognition and hand gesture detection
def update_frame():
    global frame_counter,unknown_start_time, unknown_detected, last_recognized_face     #initializing global variables

    ret, frame = cap.read()                                     # Capture the frame from the webcam
    frame = cv2.flip(frame,1)                                   #flipping frame horizontally
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)          #convert frame to RGB
    # Detect hands in the frame using a hand detector
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks 

    if ret:
        _, faces = detector.detect(frame)                       #detecting faces in the current frame
        if faces is not None and len(faces) > 0:
            #when faces are detected
            for face in faces:
                # Extract bounding box coordinates
                x, y, w, h = face[0:4].astype(int)
                xmax= x+w
                ymax = y+h

                # Ensure the coordinates are valid and within the frame bounds
                x, y, w, h = max(0, x), max(0, y), max(1, w), max(1, h)

                # Extract face region (ROI) from the frame
                out_image = frame[y:ymax, x:xmax]

                # Save the face region as a temporary image
                cv2.imwrite(temp_image_path, out_image)

                try:
                    # Use DeepFace to perform face recognition
                    res = DeepFace.find(img_path=temp_image_path, db_path=db_path, enforce_detection=False, model_name="Facenet", silent= True)
                    #when faces are recognized
                    if len(res[0]) > 0: 
                        name = os.path.splitext(os.path.basename(res[0]['identity'][0]))[0].split("_")[0].capitalize()                            # extract name 
                        cv2.rectangle(frame, (x, y), (xmax, ymax), (0, 255, 0), 2)                              #drawing green bounding rectangle
                        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)    #printing the name of the person
                        
                        #detect hand gesture to open the door  
                        landmarks_list = []                                          #creating a list to store hand landmarks
                        if hands:
                            landmarks = output.multi_hand_landmarks[0]                                  #extracting hand landmarks
                            draw_utils.draw_landmarks(frame, landmarks, mpHands.HAND_CONNECTIONS)       #drawing hand landmarks
            
                            for lm in landmarks.landmark:
                                landmarks_list.append((lm.x, lm.y))     #saving coordinates of each landmark
            
                            if hand_closed(landmarks_list) == True:
                                # If the recognized face is different from the last one, send a serial message
                                if last_recognized_face != name:  
                                    #opening the door
                                    ser.write("FACE_DETECTED".encode()) 
                                    #showing notification that the door is open
                                    show_open_door_window()
                                    
                                last_recognized_face = name
                        unknown_detected = False
                        unknown_start_time = None

                    # Unknown face is detected
                    else:
                        #showing red bounding box labeled unknown
                        cv2.rectangle(frame, (x, y), (xmax, ymax), (0, 0, 255), 2)
                        cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                        # Track how long the unknown face has been detected
                        if unknown_start_time is None:
                            unknown_start_time = time.time()
                        elif time.time() - unknown_start_time > 5:
                            # If the unknown face has been detected for more than 5 continuous seconds
                            show_add_or_open_dialog()
                            unknown_start_time = None

                except Exception as e:
                    # Handle any exceptions during the face recognition process
                    #drawing red bounding box labeled unknown
                    cv2.rectangle(frame, (x, y), (xmax, ymax), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    if unknown_start_time is None:
                        unknown_start_time = time.time()
                    elif time.time() - unknown_start_time > 5:
                        show_add_or_open_dialog()
                        unknown_start_time = None
        else:
            # No faces detected, reset unknown face tracking
            unknown_detected = False
            unknown_start_time = None
            last_recognized_face = None  # Reset the last recognized face when no face is detected

         # Convert the processed frame back to RGB format for display in the GUI
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        img = ImageTk.PhotoImage(img)

        # Update the image in the panel with the new frame
        panel.imgtk = img
        panel.config(image=img)
        # Receiving Data from all peripherals connected to Atmega8 
        receive_data()
        
    #update the frame each 50 msec
    root.after(50, update_frame)



# Initialize the main window
root = tk.Tk()
root.title("Face Recognition System")

# Add "Open Door" button
btn_open_door = tk.Button(root, text="Open Door", command=Open_Door_and_show_window)
btn_open_door.pack(side=tk.LEFT, padx=10, pady=10)

# Add "Delete Face" button
btn_delete = tk.Button(root, text="Delete Face", command=show_delete_face_dialog)
btn_delete.pack(side=tk.LEFT, padx=10, pady=10)

# Add "change password" button
btn_change_password = tk.Button(root, text="Change Password", command=show_change_password_dialog)
btn_change_password.pack(side=tk.LEFT, padx=10, pady=10)

# Add video display panel
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

root.after(10, update_frame)

root.mainloop()                     # Start the Tkinter main event loop and keeps it running

cap.release()

cv2.destroyAllWindows()