from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import numpy as np
import os

from services.ocr_service import extract_text
from services.ai_classifier import classify_route
from services.routing_service import (
    load_route_geojson,
    generate_route_between_points,
)

# ===== EXIF / GPS =====

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


# ===== 画像解析（海っぽさ判定の簡易版）=====

def detect_coastline(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((800, 800))
    arr = np.array(img)

    blue_pixels = np.sum(
        (arr[:, :, 2] > 150) &
        (arr[:, :, 2] > arr[:, :, 1]) &
        (arr[:, :, 2] > arr[:, :, 0])
    )

    ratio = blue_pixels / arr.size
    return ratio > 0.05


# ===== メイン統合 =====

def detect_route_from_image(image_path: str):
    """
    1. GPS があれば → その地点を起点に簡易ルート
    2. なければ → 画像特徴＋AI分類でルート候補
    3. 最終的に routes/ の GeoJSON を返す or 簡易LineString
    """

    # ① GPS 優先
    latlon = get_lat_lon(image_path)
    if latlon:
        lat, lon = latlon
        # ここでは簡易的に「現在地→少し先」ルートを返す
        return generate_route_between_points(
            {"lat": lat, "lon": lon},
            {"lat": lat + 0.05, "lon": lon + 0.05},
        )

    # ② GPSなし → 画像解析＋AI分類
    has_coast = detect_coastline(image_path)
    text = extract_text(image_path)  # 今は使わなくてもOK、将来拡張用
    route_label = classify_route(image_path, has_coast=has_coast, ocr_text=text)

    # ③ ラベルに対応する GeoJSON を routes/ から読み込む
    geojson = load_route_geojson(route_label)
    if geojson:
        return geojson

    # ④ フォールバック：適当な簡易ルート
    return generate_route_between_points(
        {"lat": 35.0, "lon": 139.0},
        {"lat": 35.5, "lon": 139.5},
    )