import os
import cv2
from flask import Flask, render_template_string
from ultralytics import YOLO

app = Flask(__name__)

# YOLO modelini başlatıyoruz
model = YOLO("yolo26l.pt")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>YOLO Analiz Servisi</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #121212; color: #fff; padding-top: 50px; }
        .card { background-color: #1e1e1e; display: inline-block; padding: 40px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { color: #00d26a; }
        p { color: #bbb; }
    </style>
</head>
<body>
    <div class="card">
        <h1>YOLO Analiz Servisi Aktif! 🚀</h1>
        <p>Model başarıyla yüklendi ve web sunucusu yayında.</p>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    # Render'ın dinamik atadığı PORT değişkenini alıyoruz
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)