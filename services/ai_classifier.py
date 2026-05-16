import os
from PIL import Image

MODE = os.environ.get("MODE", "local")

# ローカル用：とりあえずルールベース＋将来モデル差し替え
def _classify_local(image_path: str, has_coast: bool = False, ocr_text: str = "") -> str:
    """
    返すのは routes/ に置くファイル名に対応するラベル
    例: "tokyo_atami", "shimanami", ...
    """
    # めちゃ簡易なルールベース（あとでモデルに差し替え）
    if has_coast:
        # 海が多い → しまなみ or 東京〜熱海 など
        if "尾道" in ocr_text or "今治" in ocr_text:
            return "shimanami"
        return "tokyo_atami"
    else:
        # 内陸系なら将来別ルートに
        return "tokyo_atami"


# 本番用：AutoTrain モデルを叩く想定のダミー
def _classify_cloud(image_path: str, has_coast: bool = False, ocr_text: str = "") -> str:
    # TODO: Render 有料プラン導入時に実装（API呼び出しなど）
    return "tokyo_atami"


def classify_route(image_path: str, has_coast: bool = False, ocr_text: str = "") -> str:
    if MODE == "local":
        return _classify_local(image_path, has_coast, ocr_text)
    else:
        return _classify_cloud(image_path, has_coast, ocr_text)