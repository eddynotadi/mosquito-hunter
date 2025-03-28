from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.services.image_verification import verify_image
from app.storage import storage
from app.database import save_image, update_image, create_transaction, update_user_coins
from flask_jwt_extended import jwt_required, get_jwt_identity

image_bp = Blueprint('image', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@image_bp.route('/upload', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def upload_image():
    try:
        current_app.logger.info("Received upload request")
        
        if 'image' not in request.files:
            current_app.logger.error("No image file in request")
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
            
        file = request.files['image']
        current_app.logger.info(f"Received file: {file.filename}")
        
        if file.filename == '':
            current_app.logger.error("Empty filename")
            return jsonify({
                'success': False,
                'message': 'No selected file'
            }), 400
            
        if not allowed_file(file.filename):
            current_app.logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'
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
                'message': result['message']
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error processing upload: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500 