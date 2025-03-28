from flask import Blueprint, jsonify, request
from app.database import (
    get_leaderboard,
    get_user_transactions,
    create_transaction,
    get_user_by_username
)
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard_data():
    try:
        leaderboard = get_leaderboard()
        return jsonify(leaderboard)
    except Exception as e:
        print(f"Error fetching leaderboard: {str(e)}")
        return jsonify({"error": "Failed to fetch leaderboard data"}), 500

@user_bp.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    try:
        current_user = get_jwt_identity()
        transactions = get_user_transactions(current_user)
        return jsonify(transactions)
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        return jsonify({"error": "Failed to fetch transaction data"}), 500

@user_bp.route('/api/balance', methods=['GET'])
@jwt_required()
def get_balance():
    try:
        current_user = get_jwt_identity()
        user = get_user_by_username(current_user)
        if user:
            return jsonify({
                'coins': user.get('coins', 0),
                'kills': user.get('kills', 0)
            })
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"Error fetching balance: {str(e)}")
        return jsonify({"error": "Failed to fetch balance"}), 500 