import os
import shutil
import tempfile
from typing import Tuple

def ensure_folder(path):
    """Create folder if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def clean_filename(name):
    """Sanitize filename by removing illegal characters."""
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()

def copy_file(src, dest_folder, new_name=None):
    """Copy file to destination folder with optional new name."""
    ensure_folder(dest_folder)
    dest_path = os.path.join(dest_folder, new_name if new_name else os.path.basename(src))
    shutil.copy2(src, dest_path)
    return dest_path

def get_combined_name(*parts):
    """Join parts into a clean filename."""
    return clean_filename("_".join(str(p).strip() for p in parts if p))

def get_psd_size_from_name(name):
    """Infer PSD size from filename or user input."""
    if "1200 x 1800" in name or "shirt" in name.lower():
        return (1200, 1800)
    elif "1200 x 1200" in name or any(x in name.lower() for x in ["cap", "bag", "towel"]):
        return (1200, 1200)
    return (1200, 1800)  # Default fallback

def detect_garment_type_from_location(location_name):
    location = str(location_name).strip().upper().replace(" ","-")

    canvas_1800 = [
        "FULL-BACK", "FULL-FRONT", "LEFT-BICEP", "RIGHT-BICEP", "LEFT-CHEST", "RIGHT-CHEST",
        "LEFT-COLLAR", "RIGHT-COLLAR", "LEFT-CUFF", "RIGHT-CUFF", "LEFT-HIP", "RIGHT-HIP",
        "LEFT-SLEEVE", "RIGHT-SLEEVE", "LEFT-THIGH-HIGH", "RIGHT THIGH-HIGH", "ON-POCKET",
        "BACK-YOKE", "FULL-BACK & FULL-FRONT", "LEFT-BICEP-RIGHT-BICEP", "LEFT-CHEST-LEFT-BICEP-RIGHT-BICEP",
        "LEFT-CHEST-RIGHT-BICEP", "LEFT-CHEST-RIGHT-SLEEVE", "LEFT-SLEEVE-RIGHT-SLEEVE",
        "RIGHT-CHEST-LEFT-BICEP", "RIGHT-CHEST-LEFT-SLEEVE", "RIGHT-CHEST-LFT-BICEP-RIGHT-BICEP",
        "FULL-FRONT-FULL-BACK", "LEFT-CHEST-FULL-BACK", "RIGHT-CHEST-FULL-BACK"
    ]

    canvas_1200 = [
        "FRONT-CROWN", "CAP-BACK", "CAP-SIDE", "CAP-FRONT-SIDE", "LOWER-LEFT-CROWN", "LOWER-RIGHT-CROWN",
        "CORNER-ANGLED-TOWEL", "FRONT_CENTER", "FRONT (ON BAG)", "ON POCKET (ON BAG)"
    ]

    if location in canvas_1800:
        return "T-SHIRT"  # Default garment for 1200x1800
    elif location in canvas_1200:
        if "CAP" in location or "CROWN" in location:
            return "CAP"
        elif "BAG" in location:
            return "BAG"
        elif "TOWEL" in location:
            return "BLANKET"
        else:
            return "UNKNOWN"
    else:
        return "UNKNOWN"



# Mock: cv2.imread se return hone waale image array ko simulate karta hai.
class MockImage:
    def __init__(self, height, width):
        self.shape = (height, width, 3) 
        self._height = height
        self._width = width
    def __getitem__(self, key):
        if key == slice(None, 2):
            return (self._height, self._width)
        raise IndexError("MockImage only supports shape[:2] access.")

# Mock: cv2.imread function. Logo ke path se AR decide karta hai.
def mock_cv2_imread(path):
    # Aapka asli PDF image read hota, yeh sirf uske 'shape' ko simulate kar raha hai.
    path_lower = path.lower()
    if "square" in path_lower: # AR ~ 1.0
        return MockImage(height=1000, width=1000)
    elif "tall" in path_lower: # AR 2.0
        return MockImage(height=2000, width=1000)
    elif "wide" in path_lower: # AR 0.5
        return MockImage(height=500, width=1000)
    else: # Default AR 1.5
        return MockImage(height=1500, width=1000)

# Mock: pdf2image se return hone waale image object ko simulate karta hai.
class MockImageSaver:
    def save(self, file_path, format):
        pass # Simply simulating the save action

# Mock: pdf2image.convert_from_path
def mock_convert_from_path(pdf_path, first_page, last_page):
    # Sirf MockImageSaver object return karta hai.
    return [MockImageSaver()]

# Mock objects ko original names par map karna
cv2 = type('module', (object,), {'imread': mock_cv2_imread})
convert_from_path = mock_convert_from_path

# ====================================================================
# --- ORIGINAL LOGIC FUNCTIONS ---
# ====================================================================

def convert_pdf_to_png(pdf_path: str) -> str:
    """PDF ke first page ko temporary PNG file mein convert karta hai."""
    if not os.path.exists(pdf_path):
        # Agar file exist nahi karti, toh hum mock testing ke liye use create karte hain
        with open(pdf_path, 'w') as f:
             f.write(f"Mock PDF content for: {pdf_path}")

    # Mocked convert_from_path use hoga
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    
    # Temporary PNG file ka path generate karna
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    images[0].save(temp_file.name, "PNG") 
    
    # Console mein jankari print karna
    print(f"   -> PDF conversion simulated. Mock PNG path: {temp_file.name}")
    return temp_file.name

def compute_logo_size(garment_type: str, logo_path: str,location: str) -> Tuple[int, int]:
    """
    Garment type aur logo ke aspect ratio ke aadhar par target logo size nikaalta hai.
    """
    temp_logo_path = None
    try:
        # 1. PDF ko PNG mein convert karna
        temp_logo_path = convert_pdf_to_png(logo_path)
        
        # 2. Image ko read karna (Mocked function chalega)
        image = cv2.imread(temp_logo_path)
        
    except Exception as e:
        print("************************ Error during processing:", str(e))
        raise

    if image is None:
        raise ValueError(f"Logo image not found or failed to read: {temp_logo_path}")

    h, w = image.shape[:2]
    aspect_ratio = h / w if w > 0 else 1.0 
    
    # Console mein image details print karna
    print(f"   -> Image dimensions (mocked): H={h}, W={w}. Aspect Ratio (H/W): {aspect_ratio:.2f}")

    garment_type = garment_type.upper()

    # --- Garment Type ke hisaab se sizing logic ---
    target_width = 99  # Default fallback

    if garment_type in ["T-SHIRT", "SHIRT", "SCRUB TOP", "SCRUB PANT", "JACKET", "HOODIE", "SWEAT SHIRT"]:
        if location not in  ["FULL-BACK","FULL-FRONT"]:
            target_width = 99  
        else:
            target_width = 300
        if abs(aspect_ratio - 1.0) < 0.1:  # Agar logo square-ish hai
            target_width = 70
            
    elif garment_type in ["BAG", "CAP", "HAT"]:
        target_width = 250
        
    elif garment_type == "BLANKET":
        if aspect_ratio > 1.2: # Tall logo ke liye
            target_width = 66
        else: # Wide ya normal logo ke liye
            target_width = 99 
            
    # Target height calculate karna
    target_height = int(target_width * aspect_ratio)
    
    # 3. Temporary PNG file ko clean up karna
    if temp_logo_path and os.path.exists(temp_logo_path):
        os.remove(temp_logo_path)
        # print(f"   -> Mock PNG cleaned up.") # Clean up message hata diya taaki output clear rahe
        
    return (float(target_width), float(target_height))
