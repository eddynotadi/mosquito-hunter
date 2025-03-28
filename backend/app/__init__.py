from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from app.routes.image_routes import image_bp
from app.routes.user_routes import user_bp
from .database import init_db
from flask_jwt_extended import JWTManager
from .routes import main

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = True  # Enable debug mode

    # Initialize JWT
    jwt = JWTManager(app)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    # Initialize CORS with more permissive settings
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "X-Username"],
         methods=["GET", "POST", "OPTIONS"])

    # Initialize database
    init_db()

    # Register routes
    app.register_blueprint(main)

    # Test route
    @app.route('/test', methods=['GET'])
    def test():
        return jsonify({'message': 'Server is running!'})

    # Register blueprints
    app.register_blueprint(image_bp, url_prefix='/api')
    app.register_blueprint(user_bp)
    
    return app 