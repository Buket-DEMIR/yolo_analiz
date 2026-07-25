import os
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

CORS(app, origins=["*"], supports_credentials=True)
jwt = JWTManager(app)

# Veritabanı
from database import init_db
init_db()

# Blueprint'ler
from auth import auth_bp
from admin import admin_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "YOLO Admin Panel"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)