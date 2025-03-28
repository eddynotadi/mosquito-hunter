from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.storage import storage

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    user = storage.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if not user:
        return jsonify({'error': 'Username or email already exists'}), 400
    
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = storage.get_user_by_username(data['username'])
    
    if user and storage.verify_password(user, data['password']):
        access_token = create_access_token(identity=user['id'])
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'coins': user['coins'],
                'created_at': user['created_at'].isoformat()
            }
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = storage.get_user_by_id(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'coins': user['coins'],
        'created_at': user['created_at'].isoformat()
    }) 