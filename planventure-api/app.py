import os
from datetime import datetime, timedelta
from flask import Flask, jsonify
from dotenv import load_dotenv
from utils import db, jwt, cors

# Load environment variables
load_dotenv()

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///planventure.db')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_ERROR_MESSAGE_KEY = 'message'  # Use consistent error message key
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_TYPE = 'Bearer'
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@planventure.com')

class DevConfig(Config):
    """Development config."""
    DEBUG = True
    DEVELOPMENT = True

class ProdConfig(Config):
    """Production config."""
    DEBUG = False
    DEVELOPMENT = False

def create_app(config_class=DevConfig):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    cors.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    
    # Import and register blueprints
    from routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to PlanVenture API"})

    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "database": "connected" if db.engine.pool.checkedout() == 0 else "error"
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
