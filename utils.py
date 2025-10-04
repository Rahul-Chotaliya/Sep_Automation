import os
import shutil

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
