import cv2
import imutils
import numpy as np
from imutils.object_detection import non_max_suppression

haarcascades_path = cv2.data.haarcascades
face_cascade_path = haarcascades_path + "haarcascade_frontalface_default.xml"

face_cascade = cv2.CascadeClassifier(face_cascade_path)
fire_cascade = cv2.CascadeClassifier(r'D:\PyCharm Projects\GasDnW\fire_detection.xml')

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cam_1 = cv2.VideoCapture(0)
cam_2 = cv2.VideoCapture(r'D:\PyCharm Projects\GasDnW\fire.mp4')

cameras = [cam_1]

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)
violet = (128, 0, 128)


def frame_in_rect(objects, frame, title, color):
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in objects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    for (x, y, w, h) in pick:
        cv2.rectangle(frame, (x, y), (w, h), color, 2)
        cv2.putText(frame, title, (x, y - 2), cv2.FONT_HERSHEY_PLAIN, 1, 255)


def gen_video(camera_number):
    while True:
        _, frame = cameras[camera_number].read()
        frame = imutils.resize(frame, width=min(400, frame.shape[1]))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 8)
        fires = fire_cascade.detectMultiScale(frame, 1.5, 5)
        (bodies, _) = hog.detectMultiScale(frame,
                                           winStride=(6, 6),
                                           padding=(6, 6),
                                           scale=1.05)

        frame_in_rect(faces, frame, "face", green)
        frame_in_rect(fires, frame, "fire", blue)
        frame_in_rect(bodies, frame, "person", yellow)

        _, buffer = cv2.imencode('.jpg', frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(buffer) + b'\r\n')
