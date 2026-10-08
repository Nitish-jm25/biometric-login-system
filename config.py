import os


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


DATABASE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "biometric.db"
)


SECRET_KEY = "biosecure-micro-project-2026"


# LBPH face distance threshold.
# Lower = stricter.
FACE_MATCH_THRESHOLD = 70