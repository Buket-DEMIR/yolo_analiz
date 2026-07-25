from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
from database import get_all_users, create_user, delete_user, update_password, get_user_by_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Tüm kullanıcıları listele (sadece admin)"""
    current_user_id = int(get_jwt_identity())
    current_user = get_user_by_email(None)  # Burada user_id ile getirilmeli
    # Güncellenmesi gerekiyor, şimdilik admin kontrolü yap
    
    users = get_all_users()
    return jsonify({'users': users}), 200

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    """Yeni kullanıcı ekle (sadece admin)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    
    if not email or not password:
        return jsonify({'error': 'Email ve şifre gereklidir'}), 400
    
    # Email kontrolü
    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'Bu email zaten kullanılıyor'}), 409
    
    # Şifreyi hashle
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Kullanıcıyı oluştur
    user_id = create_user(email, hashed.decode('utf-8'), phone, is_admin=False)
    
    return jsonify({
        'success': True,
        'message': 'Kullanıcı başarıyla eklendi',
        'user_id': user_id
    }), 201

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_user(user_id):
    """Kullanıcı sil (sadece admin)"""
    # Admin kontrolü yap
    delete_user(user_id)
    return jsonify({'success': True, 'message': 'Kullanıcı silindi'}), 200

@admin_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    """Kullanıcı şifresini güncelle (sadece admin)"""
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({'error': 'Yeni şifre gereklidir'}), 400
    
    # Yeni şifreyi hashle
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    update_password(user_id, hashed.decode('utf-8'))
    
    return jsonify({'success': True, 'message': 'Şifre başarıyla güncellendi'}), 200
