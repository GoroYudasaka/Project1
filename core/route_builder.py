import requests
import json

from config.settings import ORS_API_KEY


def build_route(start=None, end=None, region="unknown", terrain="unknown", label=None):
    """
    ORS を使って道路ルートを生成する
    """

    # fallback（スタート/ゴールが無い場合）
    if label == "unknown" or start is None or end is None:
        return {
            "type": "Feature",
            "properties": {
                "region": region,
                "terrain": terrain,
                "note": "fallback route"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [139.0, 35.0],
                    [139.5, 35.5]
                ]
            }
        }

    # ORS API
    url = "https://api.openrouteservice.org/v2/directions/cycling-regular/geojson"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [start["lon"], start["lat"]],
            [end["lon"], end["lat"]]
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=body)
        data = res.json()

        # ORS が返した GeoJSON をそのまま返す
        data["features"][0]["properties"]["region"] = region
        data["features"][0]["properties"]["terrain"] = terrain

        return data["features"][0]

    except Exception as e:
        print("ORS error:", e)

        # fallback
        return {
            "type": "Feature",
            "properties": {
                "region": region,
                "terrain": terrain,
                "note": "ORS error fallback"
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [start["lon"], start["lat"]],
                    [end["lon"], end["lat"]]
                ]
            }
        }
        