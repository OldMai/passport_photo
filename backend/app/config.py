"""Configuration settings for the passport photo application."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Storage directories
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "storage/uploads")
PROCESSED_DIR = BASE_DIR / os.getenv("PROCESSED_DIR", "storage/processed")
PRINT_LAYOUTS_DIR = BASE_DIR / os.getenv("PRINT_LAYOUTS_DIR", "storage/print_layouts")

# File limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Allowed file types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

# Processing settings
DPI = int(os.getenv("DPI", 600))
PASSPORT_SIZE_INCHES = float(os.getenv("PASSPORT_SIZE_INCHES", 2.0))
PASSPORT_SIZE_PIXELS = int(PASSPORT_SIZE_INCHES * DPI)  # 1200 pixels at 600 DPI

# Print layout settings
PRINT_DPI = 300
PRINT_WIDTH_INCHES = 4
PRINT_HEIGHT_INCHES = 6
PRINT_WIDTH_PIXELS = PRINT_WIDTH_INCHES * PRINT_DPI  # 1200 pixels
PRINT_HEIGHT_PIXELS = PRINT_HEIGHT_INCHES * PRINT_DPI  # 1800 pixels
PRINT_PHOTO_SIZE_PIXELS = int(PASSPORT_SIZE_INCHES * PRINT_DPI)  # 600 pixels
PRINT_MARGIN_INCHES = 0.125
PRINT_MARGIN_PIXELS = int(PRINT_MARGIN_INCHES * PRINT_DPI)  # ~37 pixels

# Passport photo validation thresholds
HEAD_HEIGHT_MIN_PERCENT = 0.50  # 50% of image height
HEAD_HEIGHT_MAX_PERCENT = 0.6875  # 68.75% of image height
FACE_CENTER_MIN_X = 0.40
FACE_CENTER_MAX_X = 0.60
EYES_LEVEL_MIN_Y = 0.55
EYES_LEVEL_MAX_Y = 0.70
FACE_ANGLE_ASYMMETRY_MAX = 0.15  # 15% tolerance

# Minimum resolution
MIN_RESOLUTION = 600

# File retention
FILE_RETENTION_HOURS = int(os.getenv("FILE_RETENTION_HOURS", 24))

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,https://witty-bees-fall.loca.lt").split(",")

# Ensure storage directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
PRINT_LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
