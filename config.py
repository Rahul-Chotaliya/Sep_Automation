import os
from datetime import datetime

# Base folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "assets", "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "output")
IMAGE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "images")
PSD_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "photoshop")

# PSD size presets
PSD_SIZES = {
    "shirt": (1200, 1800),
    "cap_bag": (1200, 1200)
}

# Mandatory Excel columns
MANDATORY_COLUMNS = [
    "Product ID", "Supplier Part ID", "Supplier Color", "Decoration Code",
    "Decoration Color", "Decoration Location", "Final Image Name",
    "Supplier Name", "Location As per Word file"
]

# Timestamped log file
def get_log_file():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOGS_DIR, f"log_{ts}.txt")
