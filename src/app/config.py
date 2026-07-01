from pathlib import Path

# Project Root
ROOT_DIR = Path(__file__).resolve().parents[2]

# Model
MODEL_PATH = ROOT_DIR / "models" / "best.pt"

# Uploads
UPLOAD_DIR = ROOT_DIR / "uploads"

# Outputs
OUTPUT_DIR = ROOT_DIR / "outputs"

# Database
DATABASE_PATH = ROOT_DIR / "database" / "detections.db"

# Detection Settings
CONFIDENCE_THRESHOLD = 0.25

# Class Names
CLASS_NAMES = {
    0: "pothole",
    1: "longitudinal_crack",
    2: "lateral_crack",
    3: "alligator_crack"
}