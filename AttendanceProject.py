import cv2
import numpy as np
import face_recognition
import os
import csv
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Path to folder containing reference images
path = 'Images_Attendance'
images = []
classNames = []

# Check if the folder exists
if not os.path.exists(path):
    messagebox.showerror("Error", f"Folder '{path}' not found.")
    exit()
myList = os.listdir(path)

# Load images and corresponding class names
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Function to encode all reference images
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)
        if encode:  # Ensure there is at least one encoding
            encodeList.append(encode[0])
    return encodeList

# Load the student names from Attendance.csv
def loadStudentList(fileName):
    try:
        with open(fileName, 'r') as f:
            reader = csv.reader(f)
            students = [line[0].strip() for line in reader]
        return students
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{fileName}' not found.")
        exit()

# Write the attendance results to a new CSV
def writeAttendanceResults(students, presentSet):
    with open('Attendance_Result.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Status', 'Timestamp'])
        for student in students:
            status = 'Present' if student.upper() in presentSet else 'Absent'
            timestamp = presentSet.get(student.upper(), 'N/A')
            writer.writerow([student, status, timestamp])
    messagebox.showinfo("Success", "Attendance results saved to Attendance_Result.csv")

# Global variables
cap = None
running = False
presentSet = {}  # Dictionary to store attendance with timestamps

# Main attendance function
def start_attendance():
    global cap, running, presentSet
    running = True
    encodeListKnown = findEncodings(images)
    if not encodeListKnown:
        messagebox.showerror("Error", "No encodings found. Ensure 'Images_Attendance' contains valid face images.")
        return

    studentList = loadStudentList('Attendance.csv')
    presentSet = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Could not access the webcam.")
        return

    def update_frame():
        if not running:
            return
        success, img = cap.read()
        if not success:
            lblVideo.imgtk = None
            lblVideo.configure(image=None)
            return

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            bestMatchIndex = np.argmin(faceDis)

            if matches[bestMatchIndex] and faceDis[bestMatchIndex] < 0.6:
                name = classNames[bestMatchIndex].upper()
                if name not in presentSet:
                    presentSet[name] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    listbox.insert(END, f"{name} - Present at {presentSet[name]}")

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        lblVideo.imgtk = imgtk
        lblVideo.configure(image=imgtk)
        lblVideo.after(10, update_frame)

    update_frame()

# Stop attendance system
def stop_attendance():
    global running, presentSet
    running = False
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()
    writeAttendanceResults(loadStudentList('Attendance.csv'), presentSet)

# Initialize GUI
root = Tk()
root.title("Webcam Attendance System")
root.geometry("800x600")

# Video Frame
lblVideo = Label(root)
lblVideo.pack(pady=10)

# Buttons
btnStart = Button(root, text="Start Attendance", command=start_attendance, width=20, bg="green", fg="white")
btnStart.pack(pady=5)

btnStop = Button(root, text="Stop Attendance", command=stop_attendance, width=20, bg="red", fg="white")
btnStop.pack(pady=5)

# Attendance Log
listbox = Listbox(root, width=80, height=15)
listbox.pack(pady=10)

# Run the application
root.mainloop()
