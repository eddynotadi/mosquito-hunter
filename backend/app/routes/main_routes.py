from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..services.storage import storage
from ..services.verification import verification_service

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/api/submit', methods=['POST'])
def submit_image():
    try:
        print("Received image submission request")  # Debug log
        
        if 'image' not in request.files:
            print("No image file in request")  # Debug log
            return jsonify({
                'success': False,
                'message': 'No image file provided. Please select an image to upload.',
                'error': 'MISSING_FILE'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected. Please choose an image file.',
                'error': 'NO_FILE_SELECTED'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': f'File type not allowed. Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}',
                'error': 'INVALID_FILE_TYPE'
            }), 400
        
        # Check file size (max 5MB)
        if len(file.read()) > 5 * 1024 * 1024:
            file.seek(0)  # Reset file pointer
            return jsonify({
                'success': False,
                'message': 'File too large. Maximum size is 5MB.',
                'error': 'FILE_TOO_LARGE'
            }), 400
        
        file.seek(0)  # Reset file pointer
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            print(f"File saved to {filepath}")  # Debug log
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Failed to save the image. Please try again.',
                'error': 'SAVE_ERROR',
                'details': str(e)
            }), 500
        
        # Verify the image using the verification service
        username = request.form.get('username', 'Anonymous')
        verification_result = verification_service.verify_image(filepath, username)
        
        if not verification_result['success']:
            # Delete the file if verification failed
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify(verification_result), 400
        
        # Store the submission if verification was successful
        try:
            submission = storage.add_submission(username, filepath, verification_result['coins'])
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Failed to record your submission. Please try again.',
                'error': 'SUBMISSION_ERROR',
                'details': str(e)
            }), 500
        
        return jsonify({
            'success': True,
            'message': verification_result['message'],
            'submission': submission,
            'coins_earned': verification_result['coins'],
            'confidence': verification_result['confidence']
        }), 200
        
    except Exception as e:
        print(f"Error in submit_image: {str(e)}")  # Debug log
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.',
            'error': 'UNEXPECTED_ERROR',
            'details': str(e)
        }), 500

@main.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    try:
        username = request.headers.get('X-Username', 'Anonymous')
        profile = storage.get_user_profile(username)
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@main.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        limit = request.args.get('limit', default=10, type=int)
        leaderboard = storage.get_leaderboard(limit)
        return jsonify(leaderboard), 200
    except Exception as e:
        print(f"Error in get_leaderboard: {str(e)}")  # Debug log
        return jsonify({'message': str(e)}), 500 