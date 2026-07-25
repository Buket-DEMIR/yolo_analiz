import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Basit login API'si (veritabanı yok, test için)
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Test amaçlı: admin@yolo.com / Admin123!
    if email == 'admin@yolo.com' and password == 'Admin123!':
        return jsonify({
            'success': True,
            'message': 'Giriş başarılı',
            'user': {
                'email': email,
                'is_admin': True
            }
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Geçersiz email veya şifre'
        }), 401

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "YOLO Analiz Servisi"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return jsonify({"message": "Dashboard - Giriş yaptınız!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)