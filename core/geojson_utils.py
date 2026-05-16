def simple_geojson(start, end):
    return {
        "type": "Feature",
        "properties": {"name": "Auto Route", "color": "#00aaff"},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [start["lon"], start["lat"]],
                [end["lon"], end["lat"]],
            ],
        },
    }
    