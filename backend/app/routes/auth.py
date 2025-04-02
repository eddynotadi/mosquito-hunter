from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.storage import storage
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint with correct name
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
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

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required',
                'code': 'MISSING_CREDENTIALS'
            }), 400
            
        # TODO: Add proper user authentication
        # For now, accept any username/password
        access_token = create_access_token(identity=username)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'username': username
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed',
            'code': 'LOGIN_ERROR'
        }), 500

@auth.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user = get_jwt_identity()
        
        return jsonify({
            'success': True,
            'username': current_user
        })
        
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get profile',
            'code': 'PROFILE_ERROR'
        }), 500 