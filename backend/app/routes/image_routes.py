from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.services.image_verification import verify_image
from app.storage import storage
from app.database import save_image, update_image, create_transaction, update_user_coins
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.storage import storage_service
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint with correct name
image_routes = Blueprint('image_routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_routes.route('/upload', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def upload_image():
    try:
        current_app.logger.info("Received upload request")
        
        if 'image' not in request.files:
            current_app.logger.error("No image file in request")
            return jsonify({
                'success': False,
                'error': 'No image file provided',
                'message': 'Please select an image file',
                'code': 'NO_IMAGE'
            }), 400
            
        file = request.files['image']
        current_app.logger.info(f"Received file: {file.filename}")
        
        if file.filename == '':
            current_app.logger.error("Empty filename")
            return jsonify({
                'success': False,
                'error': 'No selected file',
                'message': 'Please select a file',
                'code': 'NO_FILE'
            }), 400
            
        if not allowed_file(file.filename):
            current_app.logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': 'Invalid file type. Allowed types: png, jpg, jpeg, gif',
                'code': 'INVALID_TYPE'
            }), 400
            
        filename = secure_filename(file.filename)
        current_app.logger.info(f"Secured filename: {filename}")
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        current_app.logger.info(f"Saving file to: {filepath}")
        
        file.save(filepath)
        
        # Verify the image
        current_app.logger.info("Starting image verification")
        result = verify_image(filepath)
        current_app.logger.info(f"Verification result: {result}")
        
        if result['success']:
            # Upload to S3
            s3_url = storage.upload_file(filepath)
            current_app.logger.info(f"Uploaded to S3: {s3_url}")
            
            # Use test user for development
            current_user = "test_user"
            
            # Save image to database
            image = save_image(current_user, s3_url)
            
            # Create transaction
            create_transaction(
                current_user,
                'EARNED',
                result['coins_earned'],
                'Mosquito kill verified'
            )
            
            # Update user's coins
            update_user_coins(current_user, result['coins_earned'])
            
            # Clean up local file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'coins_earned': result['coins_earned']
            })
        else:
            # Clean up local file
            os.remove(filepath)
            
            return jsonify({
                'success': False,
                'error': result['message'],
                'message': result['message'],
                'code': result.get('code', 'VERIFICATION_FAILED')
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error processing upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error processing image',
            'code': 'PROCESSING_ERROR'
        }), 500

@image_routes.route('/api/images/user/<username>', methods=['GET'])
def get_user_images(username):
    try:
        user_profile = storage_service.get_user_profile(username)
        return jsonify({
            'success': True,
            'images': user_profile['submissions']
        })
    except Exception as e:
        logger.error(f"Error getting user images: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user images',
            'message': 'Failed to get user images',
            'code': 'RETRIEVE_ERROR'
        }), 500 