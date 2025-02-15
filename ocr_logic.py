from PIL import Image, ImageDraw
import json
import easyocr
import numpy as np

def process_ocr_from_json(image_path, json_path, languages):
    
    # Kiểm tra xem languages có rỗng không
    if not languages:
        raise ValueError("Không có ngôn ngữ nào được chọn!")

    # Quét OCR với ngon ngữ mình chọn
    reader = easyocr.Reader(languages, gpu=False)

    # Load file Json do mình chọn
    with open(json_path, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    results = {}

    for shape in json_data.get("shapes", []):
        label = shape["label"]
        points = shape["points"]

        # Chuyển đổi polygon points thành bounding box
        x_coordinates = [point[0] for point in points]
        y_coordinates = [point[1] for point in points]
        min_x, max_x = min(x_coordinates), max(x_coordinates)
        min_y, max_y = min(y_coordinates), max(y_coordinates)
        bounding_box = (min_x, min_y, max_x, max_y)

        # Vẽ quanh vùng quét
        draw.rectangle(bounding_box, outline="red", width=2)

        # Crop và trích xuất OCR
        cropped_image = image.crop(bounding_box)
        cropped_image_np = np.array(cropped_image)
        ocr_result = reader.readtext(cropped_image_np)
        extracted_text = " ".join([item[1] for item in ocr_result])

        # Lưu kết quả
        results[label] = extracted_text

    # Trả về ảnh với box đã vẽ và kết quả OCR
    return image, results
