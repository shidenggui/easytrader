import pytesseract
from PIL import Image


def captcha_recognize(img_path):
    im = Image.open(img_path).convert("L")
    # 1. threshold the image
    threshold = 200
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    out = im.point(table, '1')
    # out.show()
    # 2. recognize with tesseract
    num = pytesseract.image_to_string(out)
    return num