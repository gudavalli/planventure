import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, g
from dotenv import load_dotenv
from extensions import db, jwt, cors
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity

# Load environment variables
load_dotenv()

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'this-is-a-very-long-secret-key-at-least-32-bytes')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQL Server connection string with connection pooling and encryption
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'this-is-a-secret-key-for-jwt-at-least-32-bytes-long')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_ERROR_MESSAGE_KEY = 'message'  # Use consistent error message key
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ALGORITHM = 'HS256'  # Explicitly set the algorithm
    JWT_IDENTITY_CLAIM = 'sub'  # Ensure consistent identity claim
    
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

class TestConfig(Config):
    """Test config."""
    TESTING = True
    DEBUG = True
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable CSRF tokens in testing
    WTF_CSRF_ENABLED = False

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

    # Register JWT token loader
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Convert user object to JSON serializable format."""
        if isinstance(user, dict):
            return str(user.get('id'))
        if hasattr(user, 'id'):
            return str(user.id)
        return str(user)

    # Register callback function to load user from token
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from database using JWT identity."""
        from models import User
        identity = jwt_data["sub"]
        user = db.session.get(User, int(identity))
        if user:
            g.user = user
        return user

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to PlanVenture Account Service"})

    @app.route('/health')
    def health_check():
        """Health check endpoint with database connectivity verification."""
        db_status = {
            "status": "error",
            "type": "unknown",
            "details": None
        }
        
        try:
            # Execute a simple query to check database connectivity
            from sqlalchemy import text
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            
            # Use database-specific version query
            if 'mssql' in db_url:
                version_query = text('SELECT @@version')
                db_type = "Microsoft SQL Server"
            elif 'sqlite' in db_url:
                version_query = text('SELECT sqlite_version()')
                db_type = "SQLite"
            else:
                version_query = text('SELECT version()')
                db_type = "Unknown"
                
            result = db.session.execute(version_query).scalar()
            
            db_status = {
                "status": "connected",
                "type": db_type,
                "version": result if result else "Unknown",
                "details": None
            }
            
        except Exception as e:
            db_status = {
                "status": "error",
                "type": "Unknown",
                "details": str(e)
            }
            
        return jsonify({
            "status": "healthy" if db_status["status"] == "connected" else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "api_version": "1.0.0"
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
