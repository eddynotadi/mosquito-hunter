from datetime import datetime
import threading
import os
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self._lock = threading.Lock()  # Thread-safe operations
        self.users = {}  # Store user data
        self.submissions = []  # Store all submissions
        self.next_submission_id = 1
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = {'png', 'jpg', 'jpeg'}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            logger.info(f"Created upload folder: {self.upload_folder}")

    def add_submission(self, username, image_path, coins):
        with self._lock:
            submission = {
                'id': self.next_submission_id,
                'username': username,
                'image_path': image_path,
                'coins': coins,
                'date': datetime.now().isoformat()
            }
            self.submissions.append(submission)
            self.next_submission_id += 1

            # Create or update user profile
            if username not in self.users:
                self.users[username] = {
                    'username': username,
                    'balance': 0,
                    'submissions': [],
                    'totalKills': 0,
                    'rank': len(self.users) + 1
                }

            user = self.users[username]
            user['balance'] += coins
            user['totalKills'] += 1
            user['submissions'].append(submission)

            # Update ranks for all users
            self._update_ranks()

            return submission

    def get_user_profile(self, username):
        with self._lock:
            if username not in self.users:
                self.users[username] = {
                    'username': username,
                    'balance': 0,
                    'submissions': [],
                    'totalKills': 0,
                    'rank': len(self.users) + 1
                }
            return self.users[username]

    def get_leaderboard(self, limit=10):
        with self._lock:
            # Sort users by balance (coins) in descending order
            sorted_users = sorted(
                self.users.values(),
                key=lambda x: (x['balance'], x['totalKills']),
                reverse=True
            )
            
            # Return top users with rank
            leaderboard = [{
                'id': idx + 1,
                'username': user['username'],
                'coins': user['balance'],
                'kills': user['totalKills']
            } for idx, user in enumerate(sorted_users[:limit])]
            
            return leaderboard

    def _update_ranks(self):
        # Sort users by balance and update their ranks
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: (x['balance'], x['totalKills']),
            reverse=True
        )
        
        for idx, user in enumerate(sorted_users):
            user['rank'] = idx + 1

    def allowed_file(self, filename):
        """Check if the file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_image(self, file, filename):
        """Save the uploaded image file."""
        try:
            logger.debug(f"Attempting to save file: {filename}")
            
            if not file:
                logger.error("No file provided")
                raise ValueError("No file provided")
            
            if not self.allowed_file(filename):
                logger.error(f"Invalid file type: {filename}")
                raise ValueError(f"Invalid file type. Allowed types are: {', '.join(self.allowed_extensions)}")
            
            # Check file size
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            
            if size > self.max_file_size:
                logger.error(f"File too large: {size} bytes")
                raise ValueError(f"File too large. Maximum size is {self.max_file_size/1024/1024}MB")
            
            # Secure the filename
            secure_name = secure_filename(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_filename = f"{timestamp}_{secure_name}"
            
            # Save the file
            filepath = os.path.join(self.upload_folder, final_filename)
            file.save(filepath)
            logger.info(f"File saved successfully: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

# Create a singleton instance
storage_service = StorageService()

# Export the save_image function
def save_image(file, filename):
    return storage_service.save_image(file, filename) 