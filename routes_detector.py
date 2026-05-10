from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import numpy as np
import requests

# -----------------------------
# EXIF（GPS）関連
# -----------------------------
def get_exif(image_path):
    img = Image.open(image_path)
    exif = img._getexif()
    if not exif:
        return None
    exif_data = {}
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        exif_data[tag] = value
    return exif_data


def get_gps_info(exif_data):
    if "GPSInfo" not in exif_data:
        return None

    gps_info = {}
    for key in exif_data["GPSInfo"].keys():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = exif_data["GPSInfo"][key]
    return gps_info


def convert_to_degrees(value):
    d = value[0][0] / value[0][1]
    m = value[1][0] / value[1][1]
    s = value[2][0] / value[2][1]
    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(image_path):
    exif = get_exif(image_path)
    if not exif:
        return None

    gps = get_gps_info(exif)
    if not gps:
        return None

    lat = convert_to_degrees(gps["GPSLatitude"])
    if gps["GPSLatitudeRef"] != "N":
        lat = -lat

    lon = convert_to_degrees(gps["GPSLongitude"])
    if gps["GPSLongitudeRef"] != "E":
        lon = -lon

    return lat, lon


# -----------------------------
# 逆ジオコーディング
# -----------------------------
def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    res = requests.get(url, headers={"User-Agent": "cycling-app"})
    data = res.json()
    return data.get("address", {}).get("state")


# -----------------------------
# 海岸線検出（STEP1）
# -----------------------------
def detect_coastline(image_path):
    img = Image.open(image_path).convert("RGB")

    # Render のメモリ対策として縮小
    img = img.resize((800, 800))

    arr = np.array(img)

    # 青成分が強いピクセルをカウント
    blue_pixels = np.sum(
        (arr[:, :, 2] > 150) &
        (arr[:, :, 2] > arr[:, :, 1]) &
        (arr[:, :, 2] > arr[:, :, 0])
    )

    ratio = blue_pixels / arr.size
    return ratio > 0.05  # 5%以上青なら海と判定


# -----------------------------
# 東京〜熱海ルート（仮のGeoJSON）
# -----------------------------
def tokyo_atami_route():
    return {
        "type": "Feature",
        "properties": {"name": "Tokyo-Atami Route", "color": "#ff5500"},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [139.767, 35.681],  # 東京駅
                [139.75, 35.60],
                [139.70, 35.50],
                [139.65, 35.40],
                [139.60, 35.30],
                [139.55, 35.20],
                [139.50, 35.15],
                [139.48, 35.10],  # 熱海付近
            ],
        },
    }


# -----------------------------
# メイン：GPS → 画像解析
# -----------------------------
def detect_route_from_image(image_path):
    # ① GPS がある場合は GPS 優先
    latlon = get_lat_lon(image_path)
    if latlon:
        lat, lon = latlon
        prefecture = reverse_geocode(lat, lon)

        if prefecture == "静岡県":
            return tokyo_atami_route()

        # デフォルト
        return {
            "type": "Feature",
            "properties": {"name": prefecture, "color": "#00aaff"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [lon, lat],
                    [lon + 0.01, lat + 0.01],
                ],
            },
        }

    # ② GPS がない → 画像解析（STEP1）
    has_coast = detect_coastline(image_path)

    score = 0
    if has_coast:
        score += 40

    # 東京〜熱海ルートの可能性が高い
    if score >= 40:
        return tokyo_atami_route()

    # ③ スコアが低い → 候補ルートを返す
    return {
        "suggestions": [
            {"id": 1, "name": "東京〜熱海ルート"},
            {"id": 2, "name": "湘南海岸ルート"},
            {"id": 3, "name": "房総半島ルート"},
        ]
    }