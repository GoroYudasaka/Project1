import os
import json

MODE = os.environ.get("MODE", "local")

ROUTES_DIR = "routes"


def load_route_geojson(name: str):
    """
    routes/<name>.geojson を読み込む
    例: name="tokyo_atami" → routes/tokyo_atami.geojson
    """
    filename = f"{name}.geojson"
    path = os.path.join(ROUTES_DIR, filename)
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ローカル用：疑似ルート（直線）
def _generate_route_local(start: dict, end: dict):
    return {
        "type": "Feature",
        "properties": {
            "name": "Simple Route",
            "color": "#00aaff",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [start["lon"], start["lat"]],
                [end["lon"], end["lat"]],
            ],
        },
    }


# 本番用：OpenRouteService を叩く想定のダミー
def _generate_route_cloud(start: dict, end: dict):
    # TODO: Render 有料プラン導入時に実装
    # ORS API を呼んで実際の自転車ルートを取得する
    return _generate_route_local(start, end)


def generate_route_between_points(start: dict, end: dict):
    if MODE == "local":
        return _generate_route_local(start, end)
    else:
        return _generate_route_cloud(start, end)