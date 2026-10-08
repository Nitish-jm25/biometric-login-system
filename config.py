import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

# Create the data directory if it does not exist
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "biometric.db")

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-only-secret-change-me"
)

FACE_MATCH_THRESHOLD = 70