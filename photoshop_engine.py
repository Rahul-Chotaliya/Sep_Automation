import win32com.client
import os
from coordinate_detector import get_rotation_angle
from logger import log_error
import cv2
import numpy as np
import tempfile
from coordinate_detector import get_arm_rotation_angle



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


def place_logo_in_photoshop(image_path, logo_path, location_name, coordinates, psd_name, output_folder):
    try:
        app = win32com.client.Dispatch("Photoshop.Application")
        app.Visible = False

        doc = app.Open(image_path)
        doc.ResizeCanvas(1200, 1800)  # You can make this dynamic later
        # Get rotation angle
        angle = get_arm_rotation_angle(image_path, location_name)
        if angle != 0:
            logo_path = rotate_logo(logo_path, angle)
        # Import logo
        logo_doc = app.Open(logo_path)
        logo_layer = logo_doc.ArtLayers[0]
        logo_doc.Selection.SelectAll()
        logo_doc.Selection.Copy()
        logo_doc.Close(2)  # SaveChanges = 2 means don't save

        doc.Paste()
        pasted_layer = doc.ArtLayers[0]
        pasted_layer.Name = f"Logo_{location_name}"

        ################################
        x, y = coordinates
        bounds = pasted_layer.Bounds  # [left, top, right, bottom]
        print("bounds>>>>>>>>>>>>>>>>>>>>>>>>>>>>",bounds)
        logo_width = bounds[2] - bounds[0]
        logo_height = bounds[3] - bounds[1]

        # Calculate center offset
        offset_x = x - (bounds[0] + logo_width / 2)
        offset_y = y - (bounds[1] + logo_height / 2)
        print("FINAL XXXXXXXXXXXXXXXXXX---------->>>>>>",offset_x)
        print("FINAL YYYYYYYYYYYYYYYYYY---------->>>>>>",offset_y)
        pasted_layer.Translate(offset_x, offset_y)
        ################################
        # Move logo to coordinates
        # x, y = coordinates
        # bounds = pasted_layer.Bounds  # [left, top, right, bottom]
        # print("bounds>>>>>>>>>>>>>>>>>>>>>>>>>>>>",bounds)
        # logo_width = bounds[2] - bounds[0]
        # logo_height = bounds[3] - bounds[1]
        # print("FINAL XXXXXXXXXXXXXXXXXX---------->>>>>>",x - bounds[0])
        # print("FINAL YYYYYYYYYYYYYYYYYY---------->>>>>>",y - bounds[1])
        # pasted_layer.Translate(x - bounds[0], y - bounds[1])

        # Save PSD
        psd_path = os.path.join(output_folder, f"{psd_name}.psd")
        options = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
        doc.SaveAs(psd_path, options, True)

        return doc  # Return doc for further export

    except Exception as e:
        log_error(f"Photoshop error for {psd_name}: {e}")
        return None
