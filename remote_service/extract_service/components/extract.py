import os, pymupdf  # import the bindings
from PIL import Image
from PIL import ImageOps
from typing import List

TEMP_DATA_PATH = os.path.basename(__file__).replace("components",".temp_data")

def pdf2imgs(
        pdf_path: str, 
        resize: bool = False
    )->List[str]:
    doc = pymupdf.open(pdf_path)

    img_out_paths = []
    for page in doc:
        pix = page.get_pixmap()
        img = pix.pil_image()

        if resize:
            img = img.resize((336, 336))

        curr_img_path = f"{TEMP_DATA_PATH}/page-{page.number}.png"
        img.save(curr_img_path, format = "JPEG")
        img_out_paths.append(curr_img_path)

    return img_out_paths
