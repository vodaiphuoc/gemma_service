import os, pymupdf  # import the bindings
from PIL import Image
from PIL import ImageOps
from typing import List
import base64

TEMP_DATA_PATH = os.path.dirname(__file__).replace("components",".temp_data")

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
            img = img.resize((896,  896))
        
        curr_img_path = f"{TEMP_DATA_PATH}/page-{page.number}.png"
        img.save(curr_img_path, format = "JPEG")
        img_out_paths.append(curr_img_path)
        
    return img_out_paths


def read_image(img_path:str):
    with open(img_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return "data:image/jpeg:base64,"+encoded_string