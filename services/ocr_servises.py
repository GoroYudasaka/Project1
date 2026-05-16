import os
from PIL import Image

MODE = os.environ.get("MODE", "local")

# ローカル用
def _extract_text_local(image_path: str) -> str:
    try:
        import pytesseract
    except ImportError:
        return ""

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng")
    return text


# 本番用（Render）：Google Vision を使う想定のダミー
def _extract_text_cloud(image_path: str) -> str:
    # TODO: Render 有料プラン導入時に実装
    # ここではインターフェースだけ用意しておく
    return ""


def extract_text(image_path: str) -> str:
    if MODE == "local":
        return _extract_text_local(image_path)
    else:
        return _extract_text_cloud(image_path)