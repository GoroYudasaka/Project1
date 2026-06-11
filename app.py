from flask import Flask, request, jsonify, render_template
import os
from core.detector import detect_route

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def index():
    return render_template("index.html")   # ← UI を返す


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "ファイルがありません"}), 400

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    result = detect_route(filepath)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# test

