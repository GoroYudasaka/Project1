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