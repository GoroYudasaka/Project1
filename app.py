from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from routes_detector import detect_route_from_image

app = Flask(__name__)

# アップロード先
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 許可する拡張子
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "JPG", "JPEG"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "ファイルがありません"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "ファイル名が空です"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "JPEG 形式のみ対応しています"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # ここで AI によるルート判定（現在はダミー実装）
    route_geojson = detect_route_from_image(filepath)

    # フロント側で Leaflet にそのまま渡せるように GeoJSON を返す
    return jsonify(route_geojson)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)