def detect_route_from_image(image_path: str) -> dict:
    """
    本来はここで画像からルートを推定する。
    今はダミーとして、東京駅〜熱海駅あたりの適当なラインを GeoJSON で返す。
    """

    # LineString の GeoJSON（座標は [経度, 緯度]）
    # 例: 東京駅付近 → 熱海駅付近（かなりざっくり）
    return {
        "type": "Feature",
        "properties": {
            "name": "Tokyo to Atami (dummy)",
            "color": "#ff0000",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [139.767125, 35.681236],  # 東京駅
                [139.70, 35.60],
                [139.60, 35.50],
                [139.50, 35.30],
                [139.08, 35.09],         # 熱海駅あたり
            ],
        },
    }