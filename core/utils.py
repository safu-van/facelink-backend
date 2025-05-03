import os
import uuid
import cv2
import face_recognition

from django.conf import settings
from datetime import datetime


def recognize_face(image_path):
    # Check face in the uploaded image
    try:
        image = face_recognition.load_image_file(image_path)
        image_encoding = face_recognition.face_encodings(image)[0]
    except IndexError:
        return {"matched": False}

    # IP Cameras to check
    ip_cameras = [
        ("Cam 1", "rtsp://10.12.15.168:8080/h264.sdp"),
        ("Cam 2", "rtsp://10.12.15.170:8080/h264.sdp"),
    ]

    for cam_name, cam_url in ip_cameras:
        cap = cv2.VideoCapture(cam_url, cv2.CAP_FFMPEG)

        try:
            if not cap.isOpened():
                continue

            for i in range(10):
                ret, frame = cap.read()
                if not ret:
                    continue

                rgb_frame = frame[:, :, ::-1]
                small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
                encodings = face_recognition.face_encodings(small_frame)

                for encoding in encodings:
                    match = face_recognition.compare_faces(
                        [image_encoding], encoding, tolerance=0.5
                    )
                    if match[0]:
                        # Get current date and time
                        matched_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Save matched sanpshot
                        matched_img_filename = f"match_{uuid.uuid4()}.jpg"
                        matched_img_path = os.path.join(
                            settings.MEDIA_ROOT, matched_img_filename
                        )
                        cv2.imwrite(matched_img_path, frame)

                        return {
                            "matched": True,
                            "matched_image_url": f"{settings.MEDIA_URL}{matched_img_filename}",
                            "camera": cam_name,
                            "matched_at": matched_time,
                        }
        finally:
            cap.release()

    return {"matched": False}
