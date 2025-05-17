"""JWT initialization."""
from flask_jwt_extended import JWTManager, create_access_token
from models import User, db
from flask import jsonify, current_app

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    """Convert user object to JSON serializable format."""
    if isinstance(user, User):
        return str(user.id)
    if isinstance(user, (int, str)):
        return str(user)
    return None

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Load user from database using JWT identity."""
    try:
        identity = jwt_data["sub"]
        if identity is not None:
            # Convert string ID back to integer
            user_id = int(identity)
            user = db.session.get(User, user_id)
            if user:
                db.session.refresh(user)  # Ensure we have fresh data
            return user
    except (KeyError, ValueError, TypeError):
        pass
    return None

@jwt.encode_key_loader
def get_encode_key(_jwt_headers):
    """Get the key used for encoding JWTs."""
    return current_app.config['JWT_SECRET_KEY']

@jwt.decode_key_loader
def get_decode_key(_jwt_headers, _jwt_data):
    """Get the key used for decoding JWTs."""
    return current_app.config['JWT_SECRET_KEY']

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid token errors."""
    return jsonify({
        'error': 'Invalid token',
        'message': str(error)
    }), 422

@jwt.expired_token_loader
def expired_token_callback(_jwt_header, jwt_data):
    """Handle expired token errors."""
    return jsonify({
        'error': 'Token has expired',
        'message': 'Please log in again'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(_jwt_header, jwt_data):
    """Handle non-fresh token errors."""
    return jsonify({
        'error': 'Fresh token required',
        'message': 'Please log in again'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(_jwt_header, jwt_data):
    """Handle revoked token errors."""
    return jsonify({
        'error': 'Token has been revoked',
        'message': 'Please log in again'
    }), 401

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
