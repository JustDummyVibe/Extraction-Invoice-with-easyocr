from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from PIL import Image, ImageEnhance

def sharpen_image(image_path):
    # Mở ảnh
    image = Image.open(image_path)

    # Kiểm tra kích thước ảnh
    target_size = (960, 1280)  
    if image.size != target_size:  
        image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Làm nét ảnh
    enhancer = ImageEnhance.Sharpness(image)
    sharpened_image = enhancer.enhance(2.0)

    return sharpened_image
