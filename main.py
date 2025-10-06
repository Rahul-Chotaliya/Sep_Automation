import os
from excel_reader import read_excel
from image_locator import find_image, find_logo
from coordinate_detector import get_location_coordinates
from photoshop_engine import place_logo_in_photoshop
from exporter import export_jpg
from config import PSD_OUTPUT_DIR
from utils import detect_garment_type_from_location

# === USER INPUTS ===
EXCEL_PATH = r"C:\Users\rahul\Desktop\SEP AUTOMATION\PBImageBuilderBU - 1200 x 1800 pxl.xlsx"
IMAGE_ROOT = r"C:\Users\rahul\Desktop\AUTOMATION\Images\Images"
LOGO_ROOT = r"C:\Users\rahul\Desktop\AUTOMATION\LOGO"

def run_automation():
    rows = read_excel(EXCEL_PATH)
    if not rows:
        print("No valid rows found.")
        return

    for row in rows:
        supplier_name = row["Supplier Name"]
        part_id = row["Supplier Part ID"]
        color = row["Supplier Color"]
        decoration_code = row["Decoration Code"]
        location_name = row["Decoration Location"]
        final_name = str(row["Final Image Name"]).split(".jpg")[0]

        image_path = find_image(IMAGE_ROOT, supplier_name, part_id, color)
        logo_path = find_logo(LOGO_ROOT, decoration_code)

        if not image_path or not logo_path:
            continue

        try:
            coords = get_location_coordinates(image_path, location_name)
        except Exception as e:
            from logger import log_error
            log_error(f"Coordinate error for {final_name}: {e}")
            continue

        psd_name = f"{part_id}_{color}_{location_name}"
        location_name = str(row["Decoration Location"]).strip().upper()
        garment_type = detect_garment_type_from_location(location_name)
        doc = place_logo_in_photoshop(image_path, logo_path, location_name, coords, psd_name, PSD_OUTPUT_DIR,garment_type)

        if doc:
            export_jpg(doc, final_name)

if __name__ == "__main__":
    run_automation()
