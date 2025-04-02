from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
from .routes.main_routes import main
from .routes.auth import auth
from .routes.image_routes import image_routes
from .database import init_db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    try:
        logger.info("Creating Flask application")
        app = Flask(__name__)
        
        # Load configuration
        app.config.from_object('config')
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
        app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
        logger.debug("Configuration loaded")
        
        # Initialize extensions
        CORS(app)
        JWTManager(app)
        logger.debug("Extensions initialized")
        
        # Initialize database
        init_db()
        logger.debug("Database initialized")
        
        # Register blueprints
        app.register_blueprint(main)
        app.register_blueprint(auth)
        app.register_blueprint(image_routes)
        logger.debug("Blueprints registered")
        
        # Error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            logger.warning(f"404 error: {error}")
            return jsonify({
                'success': False,
                'error': 'Not found',
                'code': 'NOT_FOUND'
            }), 404
            
        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f"500 error: {error}")
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'code': 'SERVER_ERROR'
            }), 500
            
        logger.info("Application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise 