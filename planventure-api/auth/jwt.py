"""JWT initialization."""
from flask_jwt_extended import JWTManager
from models import User, db
from flask import jsonify

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    """Convert user object to JSON serializable format."""
    return user.id if hasattr(user, 'id') else user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from database using JWT identity."""
    identity = jwt_data["sub"]
    if identity:
        user = db.session.get(User, identity)
        if user:
            return db.session.merge(user)
    return None

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid token errors."""
    return jsonify({'error': 'Invalid token'}), 401

@jwt.expired_token_loader
def expired_token_callback(_jwt_header, _jwt_data):
    """Handle expired token errors."""
    return jsonify({'error': 'Token has expired'}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    """Handle missing token errors."""
    return jsonify({'error': 'Missing Authorization Header'}), 401

@jwt.revoked_token_loader
def revoked_token_callback(_jwt_header, _jwt_data):
    """Handle revoked token errors."""
    return jsonify({'error': 'Token has been revoked'}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(_jwt_header, _jwt_data):
    """Handle non-fresh token errors."""
    return jsonify({'error': 'Fresh token required'}), 401
