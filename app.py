import os
import sys
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'gucluJwtSecretKey123456')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'

CORS(app, origins=["*"], supports_credentials=True)
jwt = JWTManager(app)

# Blueprint'leri import et ve kaydet
try:
    from auth import auth_bp
    from admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print("✅ Blueprint'ler başarıyla kaydedildi.")
except Exception as e:
    print(f"❌ Blueprint hatası: {e}")

# Veritabanı
try:
    from database import init_db
    init_db()
    print("✅ Veritabanı başarıyla başlatıldı.")
except Exception as e:
    print(f"❌ Veritabanı hatası: {e}")

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "YOLO Analiz Servisi Aktif!",
        "endpoints": {
            "login": "/login",
            "login_api": "/api/auth/login",
            "health": "/health",
            "dashboard": "/dashboard"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Admin Panel API Çalışıyor!"})

@app.route('/login')
def login_page():
    try:
        return render_template('login.html')
    except Exception as e:
        return jsonify({"error": f"Login template error: {str(e)}"}), 404

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return jsonify({"error": f"Dashboard template error: {str(e)}"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🔗 Health check: /health")
    app.run(host="0.0.0.0", port=port)