import os
from logger import log_error

def find_image(image_root, supplier_name, part_id, color):
    target_name = f"{part_id} {color}.jpg"
    supplier_folder = os.path.join(image_root, supplier_name)

    # Try inside supplier folder
    if os.path.exists(supplier_folder):
        for root, _, files in os.walk(supplier_folder):
            if target_name in files:
                return os.path.join(root, target_name)

    # Fallback: search directly in image_root
    for root, _, files in os.walk(image_root):
        if target_name in files:
            return os.path.join(root, target_name)

    log_error(f"Image not found: {target_name}")
    return None

def find_logo(logo_root, decoration_code):
    target_name = f"{decoration_code}.pdf"
    for root, _, files in os.walk(logo_root):
        if target_name in files:
            return os.path.join(root, target_name)

    log_error(f"Logo not found: {target_name}")
    return None
