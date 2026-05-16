import cv2
import numpy as np


def classify_image(image_path, text="", coast=False):
    """
    画像の地図部分から地形を分類する
    """

    img = cv2.imread(image_path)
    h, w, _ = img.shape

    # 地図部分を切り出す（detector と同じロジック）
    top = int(h * 0.15)
    bottom = int(h * 0.75)
    map_img = img[top:bottom, :]

    # -----------------------------
    # 1. 海沿い判定（青色が多い）
    # -----------------------------
    hsv = cv2.cvtColor(map_img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_ratio = np.sum(blue_mask > 0) / blue_mask.size

    if blue_ratio > 0.10:
        return "coast"

    # -----------------------------
    # 2. 川沿い判定（細長い青）
    # -----------------------------
    edges = cv2.Canny(map_img, 80, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50,
                            minLineLength=80, maxLineGap=10)

    if lines is not None and len(lines) > 5:
        return "river"

    # -----------------------------
    # 3. 都市部判定（四角形が多い）
    # -----------------------------
    gray = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rect_count = 0
    for c in contours:
        approx = cv2.approxPolyDP(c, 5, True)
        if len(approx) == 4:
            rect_count += 1

    if rect_count > 20:
        return "urban"

    # -----------------------------
    # 4. 山岳判定（緑が多い）
    # -----------------------------
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    green_ratio = np.sum(green_mask > 0) / green_mask.size

    if green_ratio > 0.15:
        return "mountain"

    # -----------------------------
    # 5. 不明
    # -----------------------------
    return "unknown"
    