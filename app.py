import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

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
CORS(app, origins=["*"], supports_credentials=True)

# JWT Manager
jwt = JWTManager(app)

# Veritabanı bağlantısını dene
try:
    from database import init_db
    from auth import auth_bp
    from admin import admin_bp
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Veritabanını başlat
    init_db()
    print("✅ Veritabanı başarıyla başlatıldı.")
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()

# Ana sayfa
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "YOLO Analiz Servisi Aktif!",
        "endpoints": {
            "login": "/api/auth/login-page",
            "health": "/health",
            "dashboard": "/dashboard"
        }
    })

# Health check
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Admin Panel API Çalışıyor!",
        "database": "connected" if os.getenv('DATABASE_URL') else "not configured"
    })

# Login sayfası (doğrudan erişim)
@app.route('/login')
def login_redirect():
    return render_template('login.html')

# Dashboard sayfası
@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except:
        return jsonify({"error": "Dashboard template not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🔗 Health check: http://0.0.0.0:{port}/health")
    app.run(host="0.0.0.0", port=port)