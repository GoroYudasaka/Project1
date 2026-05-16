import cv2
import numpy as np
from core.ocr import extract_text, detect_region
from core.route_builder import build_route
from core.classifier import classify_image


# -----------------------------
# 1. 地図部分の切り出し
# -----------------------------
def crop_map_area(image_path):
    img = cv2.imread(image_path)
    h, w, _ = img.shape

    top = int(h * 0.15)
    bottom = int(h * 0.75)

    return img[top:bottom, :], top


# -----------------------------
# 2. スタート地点（緑の丸）検出
# -----------------------------
def detect_start_point(map_img):
    hsv = cv2.cvtColor(map_img, cv2.COLOR_BGR2HSV)

    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    return (cx, cy)


# -----------------------------
# 3. ゴール地点（チェッカーフラッグ）検出
# -----------------------------
def detect_goal_flag(map_img):
    gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    candidates = [c for c in contours if cv2.contourArea(c) > 50]
    if not candidates:
        return None

    c = max(candidates, key=lambda x: cv2.boundingRect(x)[0] + cv2.boundingRect(x)[1])
    x, y, w, h = cv2.boundingRect(c)

    return (x + w // 2, y + h // 2)


# -----------------------------
# 4. 地域ごとの中心座標
# -----------------------------
REGION_CENTER = {
    "kanto": (35.7, 139.9),
    "tokyo_atami": (35.2, 139.1),
    "shimanami": (34.3, 133.0),
    "biwaichi": (35.2, 136.1),
    "unknown": (35.0, 135.0),
}


def convert_to_latlon_region(x, y, map_img, region):
    h, w, _ = map_img.shape

    center_lat, center_lon = REGION_CENTER.get(region, REGION_CENTER["unknown"])

    lat = center_lat + (h/2 - y) * 0.0005
    lon = center_lon + (x - w/2) * 0.0005

    return lat, lon


# -----------------------------
# 5. メイン：ルート検出（ORS 対応）
# -----------------------------
def detect_route(image_path):
    map_img, offset = crop_map_area(image_path)

    # OCR → 地域推定
    text = extract_text(image_path)
    region = detect_region(text)

    # 画像分類（海沿い / 川沿い / 都市 / 山岳）
    terrain = classify_image(image_path, text=text)

    # スタート/ゴール検出
    start_xy = detect_start_point(map_img)
    goal_xy = detect_goal_flag(map_img)

    if start_xy and goal_xy:
        sx, sy = start_xy
        gx, gy = goal_xy

        start_lat, start_lon = convert_to_latlon_region(sx, sy, map_img, region)
        goal_lat, goal_lon = convert_to_latlon_region(gx, gy, map_img, region)

        # ORS で道路ルート生成
        return build_route(
            start={"lat": start_lat, "lon": start_lon},
            end={"lat": goal_lat, "lon": goal_lon},
            region=region,
            terrain=terrain
        )

    # fallback
    return build_route(label="unknown", region=region, terrain=terrain)
    