import re
from PIL import Image
import pytesseract

# 日本語OCRを有効化
pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

# よく出る地名辞書（必要に応じて増やせる）
PLACE_KEYWORDS = {
    "kanto": ["柏", "松戸", "浦安", "江戸川", "東京湾", "千葉", "船橋", "市川"],
    "tokyo_atami": ["小田原", "熱海", "真鶴", "湯河原", "江ノ島", "茅ヶ崎", "大磯"],
    "shimanami": ["尾道", "今治", "向島", "因島", "生口島", "大三島", "伯方島"],
    "biwaichi": ["琵琶湖", "大津", "彦根", "長浜", "近江八幡"],
}


def extract_text(image_path):
    """
    OCRで画像から文字を抽出（日本語対応）
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="jpn+eng")
        return text
    except Exception as e:
        print("OCR error:", e)
        return ""


def detect_region(text):
    """
    OCR結果から地域を推定する
    """
    scores = {region: 0 for region in PLACE_KEYWORDS}

    for region, keywords in PLACE_KEYWORDS.items():
        for word in keywords:
            if word in text:
                scores[region] += 1

    # スコア最大の地域を返す
    best_region = max(scores, key=scores.get)

    if scores[best_region] == 0:
        return "unknown"

    return best_region