import win32com.client
import os
from coordinate_detector import get_rotation_angle
from logger import log_error
import cv2
import numpy as np
import tempfile
from coordinate_detector import get_arm_rotation_angle
from utils import compute_logo_size



def rotate_logo(logo_path, angle):
    image = cv2.imread(logo_path)
    if image is None:
        raise ValueError("Logo image not found!")

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(temp_file.name, rotated)
    return temp_file.name


def place_logo_in_photoshop(image_path, logo_path, location_name, coordinates, psd_name, output_folder, garment_type):
    try:
        app = win32com.client.Dispatch("Photoshop.Application")
        app.Visible = False
        canvas_size = 1800 if garment_type == "T-SHIRT" else 1200
        # Open the main image
        doc = app.Open(image_path)
        doc.ResizeCanvas(1200, canvas_size)  # You can make this dynamic later

        # Get rotation angle and rotate logo if needed
        angle = get_arm_rotation_angle(image_path, location_name)
        if angle != 0:
            logo_path = rotate_logo(logo_path, angle)

        # Import logo
        logo_doc = app.Open(logo_path)
        logo_layer = logo_doc.ArtLayers[0]
        logo_doc.Selection.SelectAll()
        logo_doc.Selection.Copy()
        logo_doc.Close(2)  # SaveChanges = 2 means don't save

        # Paste logo into main document
        doc.Paste()
        pasted_layer = doc.ArtLayers[0]
        pasted_layer.Name = f"Logo_{location_name}"

        # Set ruler units to pixels (1 = psPixels)
        original_ruler_units = app.Preferences.RulerUnits
        app.Preferences.RulerUnits = 1  # Pixels

        # Get current bounds (list: [left, top, right, bottom] in pixels)
        bounds = pasted_layer.Bounds
        logo_width = bounds[2] - bounds[0]
        logo_height = bounds[3] - bounds[1]
        print(f"Bounds: {bounds}, Logo Width: {logo_width}, Logo Height: {logo_height}")

        # Get desired size from compute_logo_size
        desired_width, desired_height = compute_logo_size(garment_type, logo_path)

        # Calculate scale percentages (avoid division by zero)
        if logo_width == 0 or logo_height == 0:
            log_error(f"Invalid logo dimensions for {psd_name}: width={logo_width}, height={logo_height}")
            return None

        # For proportional scaling (recommended for logos), use width-based scale
        scale = (desired_width / logo_width) * 100
        # For non-proportional, uncomment below and comment the proportional line
        # width_scale = (desired_width / logo_width) * 100
        # height_scale = (desired_height / logo_height) * 100

        # Resize the pasted layer (use proportional scaling; AnchorPosition.MiddleCenter = 5)
        pasted_layer.Resize(scale, scale, 5)  # 5 = psMiddleCenter
        # For non-proportional: pasted_layer.Resize(width_scale, height_scale, 5)

        # Recalculate bounds after resizing
        bounds = pasted_layer.Bounds
        new_width = bounds[2] - bounds[0]
        new_height = bounds[3] - bounds[1]
        print(f"New Width: {new_width}, New Height: {new_height}")

        # Calculate translation to place logo center at coordinates
        x, y = coordinates
        offset_x = x - (bounds[0] + new_width / 2)
        offset_y = y - (bounds[1] + new_height / 2)
        print(f"Offset X: {offset_x}, Offset Y: {offset_y}")
        pasted_layer.Translate(offset_x, offset_y)

        # Restore original ruler units
        app.Preferences.RulerUnits = original_ruler_units

        # Save PSD
        psd_path = os.path.join(output_folder, f"{psd_name}.psd")
        options = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
        doc.SaveAs(psd_path, options, True)

        return doc  # Return doc for further export

    except Exception as e:
        log_error(f"Photoshop error for {psd_name}: {e}")
        return None
