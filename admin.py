from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
from database import get_all_users, create_user, delete_user, update_password, get_user_by_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    users = get_all_users()
    return jsonify({'users': users}), 200

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', '')
    
    if get_user_by_email(email):
        return jsonify({'error': 'Bu email zaten kullanılıyor'}), 409
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_id = create_user(email, hashed.decode('utf-8'), phone)
    return jsonify({'success': True, 'user_id': user_id}), 201

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_user(user_id):
    delete_user(user_id)
    return jsonify({'success': True}), 200

@admin_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    data = request.get_json()
    new_password = data.get('new_password')
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    update_password(user_id, hashed.decode('utf-8'))
    return jsonify({'success': True}), 200