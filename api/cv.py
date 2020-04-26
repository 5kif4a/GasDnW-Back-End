import cv2

face_cascade = cv2.CascadeClassifier(r'D:\PyCharm Projects\GasDnW\haarcascade_frontalface_default.xml')
cam_1 = cv2.VideoCapture(0)
# cam_2 = cv2.VideoCapture(1)
cameras = [cam_1]


def gen_video(camera_number):
    while True:
        _, frame = cameras[camera_number].read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv2.putText(frame, "person", (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, 255)

        _, buffer = cv2.imencode('.jpg', frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(buffer) + b'\r\n')
