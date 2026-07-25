import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Basit sağlık kontrolü
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "YOLO Analiz Servisi Aktif",
        "endpoints": {
            "login": "/login",
            "health": "/health"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)