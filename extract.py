import sys, pymupdf  # import the bindings
from PIL import Image
from PIL import ImageOps


doc = pymupdf.open("CV_mau.pdf")  # open document


for page in doc:  # iterate through the pages
    pix = page.get_pixmap()  # render page to an image
    img = pix.pil_image()

    img = img.resize((336, 336))

    # img = ImageOps.pad(img, (336, 336), color=(0, 0, 0))
    img.save(f"page-{page.number}.png", format = "PNG")
