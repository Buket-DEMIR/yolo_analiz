from flask import Blueprint, request, jsonify, render_template, make_response
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies
import bcrypt
from database import get_user_by_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Geçersiz email veya şifre'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Geçersiz email veya şifre'}), 401
    
    token = create_access_token(identity=str(user['id']))
    response = make_response(jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'is_admin': user['is_admin']
        }
    }))
    response.set_cookie('access_token_cookie', token, httponly=True)
    return response

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = make_response(jsonify({'success': True}))
    unset_jwt_cookies(response)
    return response

@auth_bp.route('/login-page')
def login_page():
    return render_template('login.html')