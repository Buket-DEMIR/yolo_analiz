from flask import Blueprint, request, jsonify, render_template, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
import bcrypt
from database import get_user_by_email, log_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        print("🔐 Login isteği alındı")
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        if not email or not password:
            return jsonify({'error': 'Email ve şifre gereklidir'}), 400
        
        user = get_user_by_email(email)
        if not user or not user['is_active']:
            log_login(None, ip, user_agent, False)
            return jsonify({'error': 'Geçersiz email veya şifre'}), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            log_login(user['id'], ip, user_agent, False)
            return jsonify({'error': 'Geçersiz email veya şifre'}), 401
        
        log_login(user['id'], ip, user_agent, True)
        access_token = create_access_token(identity=str(user['id']), additional_claims={'is_admin': user['is_admin']})
        
        response = make_response(jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'is_admin': user['is_admin']
            }
        }))
        response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False, samesite='Lax')
        print(f"✅ Başarılı giriş: {email}")
        return response
    except Exception as e:
        print(f"❌ Login hatası: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Sunucu hatası: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = make_response(jsonify({'success': True}))
    unset_jwt_cookies(response)
    return response

@auth_bp.route('/login-page')
def login_page():
    return render_template('login.html')