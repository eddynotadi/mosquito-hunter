from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from config import Config
import boto3
from botocore.exceptions import ClientError
from flask import current_app

class InMemoryStorage:
    def __init__(self):
        self.users = {}
        self.images = {}
        self.next_user_id = 1
        self.next_image_id = 1
        self.files = {}

    def create_user(self, username, email, password):
        if username in self.users:
            return None
        if email in [user['email'] for user in self.users.values()]:
            return None

        user = {
            'id': self.next_user_id,
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'coins': 0,
            'created_at': datetime.utcnow()
        }
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user['username'] == username:
                return user
        return None

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def verify_password(self, user, password):
        return check_password_hash(user['password_hash'], password)

    def create_image(self, user_id, image_url):
        image = {
            'id': self.next_image_id,
            'user_id': user_id,
            'image_url': image_url,
            'verification_status': 'pending',
            'feedback': None,
            'coins_awarded': 0,
            'created_at': datetime.utcnow(),
            'verified_at': None
        }
        self.images[self.next_image_id] = image
        self.next_image_id += 1
        return image

    def get_user_images(self, user_id):
        return [img for img in self.images.values() if img['user_id'] == user_id]

    def get_image(self, image_id):
        return self.images.get(image_id)

    def update_image(self, image_id, **kwargs):
        if image_id in self.images:
            self.images[image_id].update(kwargs)
            return self.images[image_id]
        return None

    def update_user_coins(self, user_id, coins):
        if user_id in self.users:
            self.users[user_id]['coins'] += coins
            return self.users[user_id]
        return None

    def get_leaderboard(self, limit=100):
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: x['coins'],
            reverse=True
        )
        return sorted_users[:limit]

    def upload_file(self, filepath):
        try:
            # For testing, we'll just return a mock URL
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            mock_url = f"https://test-bucket.s3.amazonaws.com/{timestamp}_{filename}"
            
            # Store the file info in memory
            self.files[mock_url] = {
                'path': filepath,
                'timestamp': timestamp,
                'filename': filename
            }
            
            return mock_url
            
        except Exception as e:
            current_app.logger.error(f"Error uploading file: {str(e)}")
            raise

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')
        
    def upload_file(self, filepath):
        try:
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"{timestamp}_{filename}"
            
            self.s3_client.upload_file(filepath, self.bucket_name, s3_key)
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return url
            
        except ClientError as e:
            current_app.logger.error(f"Error uploading to S3: {str(e)}")
            raise

def save_image(file, filename):
    """Save the uploaded image to the upload folder."""
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    
    file_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
    file.save(file_path)
    return file_path

def update_image_status(image_id, status, coins_earned=None):
    """Update the status of an uploaded image."""
    # TODO: Implement database storage
    return True

class Storage:
    def __init__(self):
        self.submissions = []
        self.user_profiles = {}
        self.next_submission_id = 1

    def add_submission(self, username, image_path, coins):
        submission = {
            'id': self.next_submission_id,
            'username': username,
            'image_path': image_path,
            'coins': coins,
            'date': datetime.now().isoformat()
        }
        self.submissions.append(submission)
        self.next_submission_id += 1

        # Update user profile
        if username not in self.user_profiles:
            self.user_profiles[username] = {
                'username': username,
                'balance': 0,
                'submissions': [],
                'rank': len(self.user_profiles) + 1,
                'totalKills': 0
            }

        profile = self.user_profiles[username]
        profile['balance'] += coins
        profile['totalKills'] += 1
        profile['submissions'].append(submission)

        return submission

    def get_user_profile(self, username):
        if username not in self.user_profiles:
            return {
                'username': username,
                'balance': 0,
                'submissions': [],
                'rank': len(self.user_profiles) + 1,
                'totalKills': 0
            }
        return self.user_profiles[username]

# Use InMemoryStorage for development/testing
storage = InMemoryStorage() 