import os
import cv2
import torch
import threading
import pygame
from ultralytics import YOLO
import pyttsx3
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

model = YOLO("Model_path")

target_class = "Class Name "

audio_path = r"Path for audio"

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150) 
    engine.setProperty('volume', 1)  
    engine.say(text)
    engine.runAndWait()

pygame.mixer.init()
pygame.mixer.music.load(audio_path)

EMAIL_SENDER = "Sender@gmail.com" 
EMAIL_PASSWORD = "**** **** **** ****"   
EMAIL_RECEIVER = "Reciver@gmail.com" 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 

def send_email():

    subject = f"Alert: {target_class} Detected!"
    body = f"The YOLOv8 model detected a {target_class} in the camera feed."

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
       
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)  
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

cap = cv2.VideoCapture(0)

def play_audio():
    pygame.mixer.music.play()
    tts_thread = threading.Thread(target=speak_text, args=(target_class,))
    tts_thread.start()  

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(frame, device="cuda", conf=0.5)

    detected = False  
    

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            label = model.names[cls]

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            text = f"{label} {conf:.2f}"
    
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2)
            
            if label == target_class:    
                detected = True  

    if detected:
        if not pygame.mixer.music.get_busy():
            threading.Thread(target=play_audio, daemon=True).start()

        if not email_sent: 
            threading.Thread(target=send_email, daemon=True).start()
            email_sent = True
    else:
        email_sent = False 

    cv2.imshow("YOLOv8 Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

















