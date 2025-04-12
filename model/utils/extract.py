import sys, pymupdf  # import the bindings
from PIL import Image
from PIL import ImageOps

def pdf2imgs(pdf_path:str, resize: bool = False):
    doc = pymupdf.open(pdf_path)  # open document

    for page in doc:  # iterate through the pages
        pix = page.get_pixmap()  # render page to an image
        img = pix.pil_image()

        if resize:
            img = img.resize((336, 336))

        img.save(f"page-{page.number}.png", format = "PNG")