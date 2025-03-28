from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/submit', methods=['POST'])
def submit_image():
    try:
        print("Received image submission request")  # Debug log
        
        if 'image' not in request.files:
            print("No image file in request")  # Debug log
            return jsonify({'message': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        print(f"File saved to {filepath}")  # Debug log
        
        # For now, let's assume all images are valid and award 10 coins
        result = {
            'success': True,
            'coins': 10,
            'message': 'Mosquito verified successfully!'
        }
        
        # Store the submission
        username = request.form.get('username', 'Anonymous')
        submission = {
            'id': 1,
            'username': username,
            'image_path': filepath,
            'coins': result['coins'],
            'date': '2025-03-27T00:00:00'
        }
        
        return jsonify({
            'message': 'Image submitted successfully',
            'submission': submission
        }), 200
        
    except Exception as e:
        print(f"Error in submit_image: {str(e)}")  # Debug log
        return jsonify({'message': str(e)}), 500

@main.route('/user/profile', methods=['GET'])
def get_user_profile():
    try:
        username = request.headers.get('X-Username', 'Anonymous')
        profile = {
            'username': username,
            'balance': 0,
            'submissions': [],
            'rank': 1,
            'totalKills': 0
        }
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500 