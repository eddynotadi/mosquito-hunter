import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import boto3
from app.storage import storage
from app.services.image_verification import verify_mosquito_image

bp = Blueprint('images', __name__)

s3_client = boto3.client(
    's3',
    aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    user_id = get_jwt_identity()
    
    # Upload to S3
    s3_key = f'users/{user_id}/{filename}'
    s3_client.upload_fileobj(
        file,
        current_app.config['AWS_BUCKET_NAME'],
        s3_key,
        ExtraArgs={'ACL': 'public-read'}
    )
    
    # Create database entry
    image_url = f"https://{current_app.config['AWS_BUCKET_NAME']}.s3.amazonaws.com/{s3_key}"
    mosquito_image = storage.create_image(user_id, image_url)
    
    # Start async verification
    verify_mosquito_image.delay(mosquito_image['id'])
    
    return jsonify({
        'message': 'Image uploaded successfully',
        'image': mosquito_image
    }), 201

@bp.route('/my-uploads', methods=['GET'])
@jwt_required()
def get_user_uploads():
    user_id = get_jwt_identity()
    images = storage.get_user_images(user_id)
    return jsonify(images)

@bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image(image_id):
    image = storage.get_image(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404
    if image['user_id'] != get_jwt_identity():
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(image) 