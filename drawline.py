import argparse
import pickle
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw
import face_recognition
import cv2
import os
import signal
import sys
import numpy as np

DEFAULT_ENCODINGS_PATH = Path("output/encodings.pkl")
BOUNDING_BOX_COLOR = "blue"
TEXT_COLOR = "white"

def signal_handler(sig, frame):
    print("\n[INFO] Interrupted. Exiting gracefully.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def capture_image_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not found!")
        return None
    
    print("[INFO] Press 's' to capture image or 'q' to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture image.")
            break
        
        # Convert from OpenCV format (BGR) to PIL format (RGB)
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Draw landmarks on the image
        face_locations = detect_faces(pil_image)
        if len(face_locations) > 0:
            face_landmarks_list = face_recognition.face_landmarks(frame)
            draw = ImageDraw.Draw(pil_image)
            for face_landmarks in face_landmarks_list:
                draw_face_landmarks(face_landmarks, draw)

        # Convert back to OpenCV format for display
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        cv2.imshow('Press "s" to capture or "q" to quit', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            cv2.imwrite("captured_image.jpg", frame)
            print("[INFO] Image captured.")
            break
        elif key == ord('q'):
            print("[INFO] Exiting camera capture.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return pil_image

def detect_faces(img):
    # Convert PIL Image to numpy.ndarray before passing to face_recognition
    img_np = np.array(img)
    face_locations = face_recognition.face_locations(img_np)
    print(f"[INFO] Found {len(face_locations)} face(s) on the image.")
    return face_locations


def draw_face_landmarks(landmarks, draw):
    # Draw the points and lines on the face
    for feature, points in landmarks.items():
        for point in points:
            draw.ellipse([point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2], fill="blue")
        # Draw lines connecting the points
        draw.line(points, fill="blue", width=1)

def train_model_by_camera(name):
    known_encodings = []
    while True:
        print("[INFO] Capture image for training...")
        img = capture_image_from_camera()
        if img is None:
            print("[ERROR] Failed to capture image.")
            break

        face_locations = detect_faces(img)
        if len(face_locations) > 0:
            # Convert PIL Image to numpy.ndarray before passing to face_recognition
            img_np = np.array(img)
            face_encoding = face_recognition.face_encodings(img_np)[0]
            known_encodings.append(face_encoding)
            print("[INFO] Face added to model.")
       
        cv2.destroyAllWindows()

        cont = input("[INFO] Do you want to capture another image? (y/n): ").lower()
        if cont != 'y':
            break

    data = {"name": name, "encodings": known_encodings}
    model_path = f"{name}_encodings.pickle"
    with open(model_path, "wb") as file:
        pickle.dump(data, file)
    print(f"[INFO] Model saved as {model_path}")



def authenticate_user():
    name = input("[INFO] Enter your name to authenticate: ")
    model_path = f"{name}_encodings.pickle"
    if not os.path.exists(model_path):
        print("[ERROR] User not found. Please register first.")
        return

    with open(model_path, "rb") as file:
        data = pickle.load(file)
        known_encoding = data["encodings"][0]

    print("[INFO] Capture image to authenticate...")
    img = capture_image_from_camera()
    if img is None:
        print("[ERROR] Failed to capture image.")
        return

    face_locations = detect_faces(img)
    if len(face_locations) == 0:
        print("[ERROR] No face detected in the image.")
        return

    face_encoding = face_recognition.face_encodings(img)[0]
    if face_recognition.compare_faces([known_encoding], face_encoding)[0]:
        print(f"[INFO] Authentication successful! Welcome {name}.")
    else:
        print("[ERROR] Authentication failed. Face does not match.")


def main():
    action = input("[INFO] Do you want to (r)egister a new user or (a)uthenticate? (r/a): ").lower()
    if action == 'r':
        name = input("[INFO] Enter the name for the new user: ")
        train_model_by_camera(name)
    elif action == 'a':
        authenticate_user()
    else:
        print("[ERROR] Invalid choice.")

if __name__ == '__main__':
    main()
