import base64
import cv2
import numpy as np


# OpenCV's built-in Haar Cascade
CASCADE_PATH = cv2.data.haarcascades + (
    "haarcascade_frontalface_default.xml"
)

face_detector = cv2.CascadeClassifier(
    CASCADE_PATH
)


def decode_base64_image(image_data):
    """
    Convert browser base64 image into OpenCV image.
    """

    try:

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(
            image_data
        )

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        return image

    except Exception as error:

        print("Image decoding error:", error)

        return None


def detect_faces(image):
    """
    Detect faces using Haar Cascade.
    """

    if image is None:
        return []

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    return faces


def extract_face(image):
    """
    Detect exactly one face and return
    a normalized grayscale face image.
    """

    if image is None:
        return None, "Invalid image."


    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )


    if len(faces) == 0:

        return None, "No face detected. Please position your face clearly."


    if len(faces) > 1:

        return None, (
            "Multiple faces detected. "
            "Please keep only one person in the camera."
        )


    x, y, w, h = faces[0]


    face = gray[
        y:y + h,
        x:x + w
    ]


    if face.size == 0:

        return None, "Unable to extract the face."


    # Normalize face size
    face = cv2.resize(
        face,
        (200, 200)
    )


    # Improve contrast
    face = cv2.equalizeHist(
        face
    )


    return face, None


def face_to_bytes(face):
    """
    Convert face image to bytes for SQLite.
    """

    success, encoded = cv2.imencode(
        ".jpg",
        face
    )

    if not success:
        return None

    return encoded.tobytes()


def bytes_to_face(image_bytes):
    """
    Convert stored bytes back to OpenCV image.
    """

    array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    return cv2.imdecode(
        array,
        cv2.IMREAD_GRAYSCALE
    )


def create_lbph_recognizer():
    """
    Create an OpenCV LBPH recognizer.
    """

    return cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )


def calculate_confidence(distance):
    """
    Convert LBPH distance into a
    user-friendly confidence value.

    This is an approximate project score,
    not a calibrated probability.
    """

    confidence = 100 - distance

    confidence = max(
        0,
        min(100, confidence)
    )

    return round(
        confidence,
        2
    )