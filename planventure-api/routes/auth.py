from datetime import datetime, timedelta, UTC
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User
from utils import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    try:
        new_user = User(email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Update last login time
    user.last_login = datetime.now(UTC)
    db.session.commit()

    # Generate access token with fresh=True to ensure it's a new login
    try:
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string to ensure valid JWT subject
            expires_delta=timedelta(days=1),
            fresh=True
        )
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Token generation failed', 'details': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user details."""
    identity = get_jwt_identity()
    if identity is None:
        return jsonify({'error': 'Invalid token'}), 401
    
    try:
        user = db.session.execute(db.select(User).filter_by(id=identity)).scalar_one_or_none()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user's email address."""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'error': 'Invalid verification token'}), 400
        
    try:
        if user.verify_email(token):
            db.session.commit()
            return jsonify({'message': 'Email verified successfully'}), 200
        return jsonify({'error': 'Invalid or expired token'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to verify email', 'details': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
        
    try:
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # Don't reveal if email exists
            return jsonify({'message': 'If the email exists, you will receive a reset link'}), 200
            
        token = user.generate_reset_token()
        db.session.commit()
        
        reset_url = f"{request.host_url.rstrip('/')}/reset-password/{token}"
        if send_password_reset_email(user, reset_url):
            return jsonify({'message': 'Password reset instructions sent'}), 200
        
        return jsonify({'error': 'Failed to send reset email'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password with token."""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'New password is required'}), 400
        
    try:
        user = db.session.query(User).filter_by(reset_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        if not user.verify_reset_token(token):
            return jsonify({'error': 'Invalid or expired reset token'}), 400
            
        user.set_password(data['password'])
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reset password', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    """Get or update user profile."""
    identity = get_jwt_identity()
    if identity is None:
        return jsonify({'error': 'Invalid token'}), 401
    
    try:
        user = db.session.execute(db.select(User).filter_by(id=identity)).scalar_one_or_none()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if request.method == 'GET':
            return jsonify(user.to_dict()), 200
        
        # Handle PUT request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        user_data = user.to_dict()
        return jsonify(user_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    current_user_id = get_jwt_identity()
    try:
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new password are required'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500
