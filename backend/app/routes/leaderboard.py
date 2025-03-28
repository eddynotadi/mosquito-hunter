from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.storage import storage

bp = Blueprint('leaderboard', __name__)

@bp.route('/global', methods=['GET'])
def get_global_leaderboard():
    users = storage.get_leaderboard(limit=100)
    return jsonify([{
        'username': user['username'],
        'coins': user['coins'],
        'rank': rank + 1
    } for rank, user in enumerate(users)])

@bp.route('/weekly', methods=['GET'])
def get_weekly_leaderboard():
    # For testing, we'll just return the global leaderboard
    users = storage.get_leaderboard(limit=100)
    return jsonify([{
        'username': user['username'],
        'coins': user['coins'],
        'rank': rank + 1
    } for rank, user in enumerate(users)])

@bp.route('/user-rank', methods=['GET'])
@jwt_required()
def get_user_rank():
    user_id = get_jwt_identity()
    user = storage.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the user's rank
    users = storage.get_leaderboard()
    rank = next((rank + 1 for rank, u in enumerate(users) if u['id'] == user_id), 0)
    
    return jsonify({
        'username': user['username'],
        'coins': user['coins'],
        'rank': rank,
        'total_users': len(storage.users)
    }) 