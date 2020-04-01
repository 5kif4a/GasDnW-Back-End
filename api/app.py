from flask import Flask, Response, request
from flask_cors import CORS
# import cv2
import time
import random
import json

from .config import cfg

# cam_1 = cv2.VideoCapture(0)
# cam_2 = cv2.VideoCapture(1)
# cameras = [cam_1, cam_2]
#
# face_cascade = cv2.CascadeClassifier(r'D:\PyCharm Projects\GasDnW\haarcascade_frontalface_default.xml')
app = Flask(__name__)

CORS(app)
app.config.from_object(cfg)


@app.route('/mq2', methods=["GET, POST"])
def get_data_from_mq2():
    if request.method == "GET":
        return "MQ2"
    if request.method == "POST":
        print(request.get_json())
        response = app.response_class(
            response="OK",
            status=200,
            mimetype='application/json'
        )
        return response


@app.route('/dht', methods=["GET, POST"])
def get_data_from_dht():
    if request.method == "GET":
        return "dht"
    if request.method == "POST":
        print(request.get_json())
        response = app.response_class(
            response="OK",
            status=200,
            mimetype='application/json'
        )
        return response


# def gen_video(camera_number):
#     while True:
#         _, frame = cameras[camera_number].read()
#
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         faces = face_cascade.detectMultiScale(gray, 1.1, 4)
#
#         for (x, y, w, h) in faces:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
#             cv2.putText(frame, "person", (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, 255)
#
#         _, buffer = cv2.imencode('.jpg', frame)
#
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + bytearray(buffer) + b'\r\n')


# @app.route('/camera/<int:camera_number>')
# def video_feed(camera_number):
#     return Response(gen_video(camera_number), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run()
