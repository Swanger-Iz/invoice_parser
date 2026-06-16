"""This script load paddleocr models"""

import os
from pathlib import Path

# import sys
from paddleocr import PaddleOCR

files_to_check = ["inference.pdiparams", "config.json", "inference.json", "inference.yml", "README.md"]

# sys.path.insert(0, str(Path(__file__).parent.parent))


models_dir = Path(__file__).parent.parent / "models" / "temp"

models = []

for dir in os.listdir(models_dir):
    if (models_dir / dir).is_dir() and not dir.endswith("__") and not dir.startswith("__"):
        files_dir = len(os.listdir(models_dir / dir))

        models.append({"type": dir, "path": str(models_dir / dir), "exists": True if files_dir != 0 else False})

ocr_params = dict()

for model in models:
    print("Checking models")
    # Recognition
    if not model["exists"] and model["type"] == "det":
        print(f"Need download a {model['type']}")
        ocr_params["text_detection_model_dir"] = model["path"]
    # Detection
    if not model["exists"] and model["type"] == "rec":
        print(f"Need download a {model['type']}")
        ocr_params["text_recognition_model_dir"] = model["path"]
    # Doc orientation
    if not model["exists"] and model["type"] == "doc_orientation":
        print(f"Need download a {model['type']}")
        ocr_params["doc_orientation_classify_model_dir"] = model["path"]


# Donwloading and creating an OCR model!
print("Donwloading and creating an OCR model! It takes a few time")


ocr_model = PaddleOCR(
    # det config
    text_detection_model_dir=ocr_params["text_detection_model_dir"],
    text_detection_model_name="PP-OCRv5_server_det",
    text_det_box_thresh=0.5,
    text_det_thresh=0.3,
    text_det_unclip_ratio=1.6,  # расширение bbox (важно для плотного текста!)
    # rec config
    text_recognition_model_name="eslav_PP-OCRv5_mobile_rec",
    text_recognition_model_dir=ocr_params["text_recognition_model_dir"],
    # text_recognition_model_name="PP-OCRv5_server_rec",
    text_recognition_batch_size=6,
    # Классификатор поворота строк
    doc_orientation_classify_model_dir=ocr_params["doc_orientation_classify_model_dir"],
    use_doc_orientation_classify=True,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device="gpu",
)


def get_downloaded_paddleOCR():
    return ocr_model


get_downloaded_paddleOCR()
print(models)
print(ocr_params)
print("=" * 20, "Success", "=" * 20)
# print(os.listdir("models/det") == files_to_check)
