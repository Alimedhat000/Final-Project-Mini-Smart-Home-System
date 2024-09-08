import cv2
from deepface import DeepFace
import os, shutil


cap = cv2.VideoCapture(0)
db_path= "C:\\D\\mind cloud\\Tasks software\\face detection\\software\\database"

#add new face to the database
def add_to_database(name, db_path):
    img_name = name +"_.jpeg"
    img_path = os.path.join(db_path, img_name)  #creating path for the image
    cv2.imwrite(img_path, frame)                #capture image and add to the database

#delete faces from the database
def delete_faces(name, db_path):
    img_name = name +"_.jpeg"
    img_path = os.path.join(db_path, img_name)  #creating path for the image
    if os.path.isfile(img_path):
        os.remove(img_path)
    else:
        print('name does not exist')

while True:
    state, frame= cap.read()                                    #capture frame by frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)          #convert frame to RGB
    cv2.waitKey(3)
    # Save the current frame as an image (temporary)
    temp_image_path = 'temp_frame.jpg'
    cv2.imwrite(temp_image_path, frame)
    cv2.imshow("video", frame)
    

    if state == True:
        #searching for the face in database
        res = DeepFace.find(img_path= temp_image_path, db_path= db_path, enforce_detection=False, model_name="VGG-Face")
        
        if len(res[0]['identity'])>0:
            name = res[0]['identity'][0].split('\\')[7].split("_")[0]
            
            #finding dimensions of bounding box
            xmin = int(res[0]['source_x'][0])
            ymin = int(res[0]['source_y'][0])
            w = res[0]['source_w'][0]
            h = res[0]['source_h'][0]
            xmax = int(xmin + w)
            ymax = int(ymin + h)
            
            #drawing green bounding rectangle
            cv2.rectangle(frame, (xmin,ymin),(xmax,ymax), (0,255,0),2)
            
            #printing the name
            cv2.putText(frame, name,(xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0),2, cv2.LINE_AA)
            ##opening the door
            print('found'+ name)
        else:
            ##draw red rectangle
            ##give option to open with password
            ##if homeowners approve adding to database:{
            name= input('enter name of person')                          #name entered by homeowners 
            add_to_database(name, db_path)                               #add new person to the database} 
            ##elif owners aproves openning the door only : open the door
            print('not found')

        cv2.imshow("result", frame)

        #if homeowner want's to delete image:{
        #name= input('enter name of person to delete')
        #delete_faces(name, db_path)}

cv2.waitKey(1)

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()