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


db_path = (Path(__file__).resolve().parent / 'Images').as_posix()
temp_image_path = (Path(__file__).resolve().parent / 'detected_face.jpg').as_posix()

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize face detector
detector = cv2.FaceDetectorYN.create(
    model=(Path(__file__).resolve().parent / 'face_detection_yunet_2023mar.onnx').as_posix(),
    config='',
    input_size=(640, 480),
    score_threshold=0.5,
    nms_threshold=0.4
)

# Variable to track the time an unknown face has been detected
unknown_start_time = None
unknown_detected = False
last_recognized_face = None  # Track the last recognized face

# Initialize serial communication
ser = serial.Serial('COM4', 19200)

def receive_data():
    if ser.in_waiting > 0:
        received_data = ser.readline().decode('utf-8').rstrip()  # Read and decode received data
        print(f"Received from ATmega8A: {received_data}")
        
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


def delete_faces(name):
    img_name = f"{name}.jpeg"
    img_path = os.path.join(db_path, img_name)
    if os.path.isfile(img_path):
        os.remove(img_path)
        messagebox.showinfo("Success", f"{name}'s image deleted from the database.")
    else:
        messagebox.showerror("Error", f"{name} does not exist in the database.")


def show_delete_face_dialog():
    def delete_face_from_listbox(event):
        selected_name = listbox.get(listbox.curselection())
        if selected_name:
            delete_faces(selected_name)
            update_face_list()

    def update_face_list():
        listbox.delete(0, tk.END)
        for filename in os.listdir(db_path):
            if filename.endswith(".jpeg"):
                listbox.insert(tk.END, filename.split('.')[0])

    delete_window = Toplevel(root)
    delete_window.title("Delete Face")
    listbox = Listbox(delete_window)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = Scrollbar(delete_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    listbox.bind("<Double-1>", delete_face_from_listbox)
    update_face_list()


def show_add_or_open_dialog():
    choice = messagebox.askyesnocancel("Unknown Face Detected",
                                       'Unknown face detected. Do you want to add it to the database?(yes=add)(no=open the door)')

    if choice:
        name = simpledialog.askstring("Add Face", "Enter name for the new face:")
        if name:
            ret, frame = cap.read()
            if ret:
                add_to_database(name, frame)
            else:
                messagebox.showerror("Error", "Failed to capture frame.")
    elif choice is False:
        show_open_door_window()
    else:
        messagebox.showinfo("Cancelled", "Operation cancelled.")


def show_change_password_dialog():
    def save_new_password():
        new_password = password_entry.get()
        if new_password:
            global saved_password
            ser.write(f"CHANGE_PASS:{new_password}".encode())
            saved_password = new_password
            messagebox.showinfo("Success", "Password changed successfully.")
            change_password_window.destroy()  # Close the window after saving
        else:
            messagebox.showerror("Error", "No password entered.")

    global saved_password
    saved_password = ""

    change_password_window = tk.Toplevel(root)
    change_password_window.title("Change Password")

    tk.Label(change_password_window, text="Enter new password:").pack(padx=20, pady=10)

    password_entry = tk.Entry(change_password_window, show='*')
    password_entry.pack(padx=20, pady=10)

    tk.Button(change_password_window, text="Save", command=save_new_password).pack(padx=20, pady=20)


def show_open_door_window():
    open_door_window = Toplevel(root)
    open_door_window.title("Open Door")
    label = tk.Label(open_door_window, text="Door is now open!")
    label.pack(padx=20, pady=20)


def update_frame():
    global frame_counter,unknown_start_time, unknown_detected, last_recognized_face

    ret, frame = cap.read()
    if ret:
        _, faces = detector.detect(frame)
        if faces is not None and len(faces) > 0:
            for face in faces:
                x, y, w, h = face[0:4].astype(int)
                x, y, w, h = max(0, x), max(0, y), max(1, w), max(1, h)
                out_image = frame[y:y + h, x:x + w]
                cv2.imwrite(temp_image_path, out_image)
                try:
                    
                    res = DeepFace.find(img_path=temp_image_path, db_path=db_path, enforce_detection=False,
                                        model_name="Facenet", silent = True)
                    if len(res[0]) > 0:
                        name = os.path.basename(res[0]['identity'][0]).split("_")[0]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        # If the recognized face is different from the last one, send a serial message
                        if last_recognized_face != name:
                            ser.write("FACE_DETECTED".encode())
                            last_recognized_face = name
                        unknown_detected = False
                        unknown_start_time = None
                    else:
                        # Unknown face detected
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        if unknown_start_time is None:
                            unknown_start_time = time.time()
                        elif time.time() - unknown_start_time > 5:
                            # If the unknown face has been detected for more than 5 continuous seconds
                            show_add_or_open_dialog()
                            unknown_start_time = None
                except Exception as e:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
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

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        img = ImageTk.PhotoImage(img)
        panel.imgtk = img
        panel.config(image=img)
        receive_data()
        

    root.after(50, update_frame)



# Initialize the main window
root = tk.Tk()
root.title("Face Recognition System")

# Add "Open Door" button
btn_open_door = tk.Button(root, text="Open Door", command=show_open_door_window)
btn_open_door.pack(side=tk.LEFT, padx=10, pady=10)

# Add "Delete Face" button
btn_delete = tk.Button(root, text="Delete Face", command=show_delete_face_dialog)
btn_delete.pack(side=tk.LEFT, padx=10, pady=10)

btn_change_password = tk.Button(root, text="Change Password", command=show_change_password_dialog)
btn_change_password.pack(side=tk.LEFT, padx=10, pady=10)

# Add video display panel
panel = tk.Label(root)
panel.pack(padx=10, pady=10)

root.after(10, update_frame)
root.mainloop()
cap.release()

cv2.destroyAllWindows()