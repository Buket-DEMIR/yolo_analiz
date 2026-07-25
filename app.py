import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

# Kendi modüllerimiz
from database import init_db
from auth import auth_bp
from admin import admin_bp

# .env dosyasını yükle
load_dotenv()

# Flask uygulamasını oluştur
app = Flask(__name__)

# JWT Konfigürasyonu
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'gucluJwtSecretKey123456')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'

# CORS ayarları
CORS(app, origins=["http://localhost:5000", "http://localhost:3000", "https://yolo-analiz.onrender.com"], supports_credentials=True)

# JWT Manager
jwt = JWTManager(app)

# Blueprint'leri kaydet
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Veritabanını başlat
init_db()

# Ana sayfa
@app.route('/')
def home():
    return render_template('index.html') if os.path.exists('templates/index.html') else jsonify({"status": "YOLO Analiz Servisi Aktif!"})

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Admin Panel API Çalışıyor!"})

# ⭐ BURAYI EKLE ⭐
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)