// 地図の初期化
const map = L.map("map").setView([36.2048, 138.2529], 5); // 日本全体くらいのズーム

// タイルレイヤー（OpenStreetMap）
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

let currentRouteLayer = null;

// フォーム送信処理
const form = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const messageDiv = document.getElementById("message");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    messageDiv.textContent = "JPEG 画像を選択してください。";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  messageDiv.textContent = "アップロード中...";

  try {
    const res = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      messageDiv.textContent = data.error || "エラーが発生しました。";
      return;
    }

    messageDiv.textContent = "ルートを地図に描画しました。";

    // 既存ルートを削除
    if (currentRouteLayer) {
      map.removeLayer(currentRouteLayer);
    }

    // 返ってきた GeoJSON を描画
    currentRouteLayer = L.geoJSON(data.route, {
      style: function (feature) {
        return {
          color: feature.properties.color || "#ff0000",
          weight: 5,
        };
      },
    }).addTo(map);

    // ルートにズーム
    map.fitBounds(currentRouteLayer.getBounds());
  } catch (err) {
    console.error(err);
    messageDiv.textContent = "通信エラーが発生しました。";
  }
});