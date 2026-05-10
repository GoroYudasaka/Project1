from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

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
    import requests

def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    res = requests.get(url, headers={"User-Agent": "cycling-app"})
    data = res.json()
    return data.get("address", {}).get("state")  # 都道府県名
def detect_route_from_image(image_path):
    latlon = get_lat_lon(image_path)
    if not latlon:
        return {"error": "GPS情報がありません"}

    lat, lon = latlon
    prefecture = reverse_geocode(lat, lon)

    # 静岡県の例（熱海ルート）
    if prefecture == "静岡県":
        return {
            "type": "Feature",
            "properties": {"name": "Atami Route", "color": "#ff0000"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [139.07, 35.10],
                    [139.08, 35.09],
                    [139.09, 35.08],
                ],
            },
        }

    # デフォルト（適当な2点を線で結ぶ）
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
from PIL import Image
import numpy as np

def detect_coastline(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    # 青成分が強いピクセルをカウント
    blue_pixels = np.sum((arr[:,:,2] > 150) & (arr[:,:,2] > arr[:,:,1]) & (arr[:,:,2] > arr[:,:,0]))

    # 全体の何％が青か
    ratio = blue_pixels / arr.size

    return ratio > 0.05  # 5% 以上青なら海が写っていると判定
import pytesseract
import re

def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng")
    return text

def extract_distance_and_elevation(text):
    distance = None
    elevation = None

    # 124.6 km のような表記を抽出
    dist_match = re.search(r"(\d{2,3}\.\d)\s*km", text)
    if dist_match:
        distance = float(dist_match.group(1))

    # 639 m のような表記を抽出
    elev_match = re.search(r"(\d{2,4})\s*m", text)
    if elev_match:
        elevation = float(elev_match.group(1))

    return distance, elevation
def analyze_image_features(image_path):
    features = {}

    # 海岸線判定
    features["has_coastline"] = detect_coastline(image_path)

    # OCR
    text = extract_text(image_path)
    distance, elevation = extract_distance_and_elevation(text)
    features["distance"] = distance
    features["elevation"] = elevation

    # スコアリング
    score = 0

    if features["has_coastline"]:
        score += 40

    if distance and 110 <= distance <= 140:
        score += 30

    if elevation and 400 <= elevation <= 800:
        score += 20

    features["score"] = score
    return features
def detect_route_from_image(image_path):
    latlon = get_lat_lon(image_path)

    # GPS がある場合は従来通り
    if latlon:
        lat, lon = latlon
        prefecture = reverse_geocode(lat, lon)
        return route_from_prefecture(prefecture)

    # GPS がない場合 → 画像解析
    features = analyze_image_features(image_path)

    if features["score"] >= 70:
        return tokyo_atami_route()  # 東京〜熱海ルートのGeoJSON

    # スコアが低い場合は候補を返す
    return {
        "suggestions": [
            {"id": 1, "name": "東京〜熱海ルート"},
            {"id": 2, "name": "湘南海岸ルート"},
            {"id": 3, "name": "房総半島ルート"},
        ]
    }

