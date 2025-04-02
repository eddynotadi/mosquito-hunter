from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from ..services.verification import verify_image
from ..services.storage import storage_service
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/api/submit', methods=['POST'])
def submit_image():
    try:
        logger.debug("Received image submission request")
        
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({
                'success': False,
                'error': 'No image file provided',
                'message': 'Please select an image file',
                'code': 'NO_IMAGE'
            }), 400
            
        file = request.files['image']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({
                'success': False,
                'error': 'No selected file',
                'message': 'Please select a file',
                'code': 'NO_FILE'
            }), 400
            
        if not storage_service.allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'message': f'Invalid file type. Allowed types are: {", ".join(storage_service.allowed_extensions)}',
                'code': 'INVALID_TYPE'
            }), 400
            
        # Get username from request
        username = request.form.get('username')
        if not username:
            logger.error("No username provided")
            return jsonify({
                'success': False,
                'error': 'Username is required',
                'message': 'Please provide a username',
                'code': 'NO_USERNAME'
            }), 400
            
        # Save the image
        try:
            filepath = storage_service.save_image(file, file.filename)
            logger.info(f"Image saved successfully: {filepath}")
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to save image',
                'code': 'SAVE_ERROR'
            }), 500
            
        # Verify the image
        try:
            verification_result = verify_image(filepath, username)
            logger.info(f"Image verification result: {verification_result}")
        except Exception as e:
            logger.error(f"Error verifying image: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error verifying image',
                'message': 'Failed to verify image',
                'code': 'VERIFICATION_ERROR'
            }), 500
            
        if not verification_result['success']:
            # Delete the file if verification failed
            try:
                os.remove(filepath)
                logger.info(f"Deleted unverified image: {filepath}")
            except Exception as e:
                logger.error(f"Error deleting unverified image: {str(e)}")
                
            return jsonify({
                'success': False,
                'error': verification_result['message'],
                'message': verification_result['message'],
                'code': verification_result['code']
            }), 400
            
        # Add submission to storage
        submission = storage_service.add_submission(
            username=username,
            image_path=filepath,
            coins=verification_result['coins']
        )
        
        return jsonify({
            'success': True,
            'message': 'Image submitted successfully',
            'submission': submission
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in submit_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An unexpected error occurred',
            'code': 'UNKNOWN_ERROR'
        }), 500

@main.route('/api/submissions', methods=['GET'])
def get_submissions():
    try:
        username = request.args.get('username')
        if not username:
            logger.error("No username provided for submissions request")
            return jsonify({
                'success': False,
                'error': 'Username is required',
                'code': 'NO_USERNAME'
            }), 400
            
        user_profile = storage_service.get_user_profile(username)
        logger.info(f"Retrieved submissions for user: {username}")
        
        return jsonify({
            'success': True,
            'submissions': user_profile['submissions']
        })
        
    except Exception as e:
        logger.error(f"Error getting submissions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error retrieving submissions',
            'code': 'RETRIEVE_ERROR'
        }), 500

@main.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    try:
        limit = int(request.args.get('limit', 10))
        leaderboard_data = storage_service.get_leaderboard(limit)
        logger.info(f"Retrieved leaderboard with limit: {limit}")
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error retrieving leaderboard',
            'code': 'LEADERBOARD_ERROR'
        }), 500 