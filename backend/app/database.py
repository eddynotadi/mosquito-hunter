from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')

# Create MongoDB client
client = MongoClient(MONGODB_URI)

# Get database
db = client.mosquito_coin

# Collections
users = db.users
images = db.images
transactions = db.transactions
submissions = db.submissions

def init_db():
    """Initialize database with indexes and default data."""
    # Create indexes
    users.create_index('username', unique=True)
    images.create_index('user_id')
    transactions.create_index('user_id')
    transactions.create_index('timestamp')
    submissions.create_index('user_id')
    submissions.create_index('submitted_at')
    
    # Create default admin user if not exists
    if not users.find_one({'username': 'admin'}):
        users.insert_one({
            'username': 'admin',
            'password': 'admin123',  # In production, use proper password hashing
            'role': 'admin',
            'coins': 0,
            'kills': 0,
            'created_at': datetime.utcnow()
        })

def add_submission(user_id, image_path, verified=False):
    """Add a new image submission."""
    submission = {
        'user_id': user_id,
        'image_path': image_path,
        'verified': verified,
        'submitted_at': datetime.utcnow()
    }
    submissions.insert_one(submission)
    return submission

def get_user_submissions(user_id):
    """Get all submissions for a user."""
    return list(submissions.find(
        {'user_id': user_id}
    ).sort('submitted_at', -1))

def get_leaderboard():
    """Get top users by verified submissions."""
    pipeline = [
        {
            '$match': {'verified': True}
        },
        {
            '$group': {
                '_id': '$user_id',
                'submission_count': {'$sum': 1}
            }
        },
        {
            '$lookup': {
                'from': 'users',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'user'
            }
        },
        {
            '$unwind': '$user'
        },
        {
            '$project': {
                'username': '$user.username',
                'submission_count': 1,
                '_id': 0
            }
        },
        {
            '$sort': {'submission_count': -1}
        },
        {
            '$limit': 10
        }
    ]
    return list(submissions.aggregate(pipeline))

def get_user_by_username(username):
    """Get user by username."""
    return users.find_one({'username': username})

def create_user(username, password):
    """Create a new user."""
    user = {
        'username': username,
        'password': password,  # In production, hash the password
        'coins': 0,
        'kills': 0,
        'created_at': datetime.utcnow()
    }
    users.insert_one(user)
    return user

def update_user_coins(user_id, amount):
    """Update user's coin balance."""
    users.update_one(
        {'_id': user_id},
        {'$inc': {'coins': amount}}
    )

def create_transaction(user_id, type, amount, description):
    """Create a new transaction."""
    transaction = {
        'user_id': user_id,
        'type': type,
        'amount': amount,
        'description': description,
        'timestamp': datetime.utcnow()
    }
    transactions.insert_one(transaction)
    return transaction

def get_user_transactions(user_id, limit=10):
    """Get user's recent transactions."""
    return list(transactions.find(
        {'user_id': user_id}
    ).sort('timestamp', -1).limit(limit))

def save_image(user_id, image_url, verification_status='pending'):
    """Save image information."""
    image = {
        'user_id': user_id,
        'image_url': image_url,
        'verification_status': verification_status,
        'feedback': '',
        'coins_awarded': 0,
        'created_at': datetime.utcnow()
    }
    images.insert_one(image)
    return image

def update_image(image_id, **kwargs):
    """Update image information."""
    images.update_one(
        {'_id': image_id},
        {'$set': kwargs}
    ) 