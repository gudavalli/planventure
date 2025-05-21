from datetime import datetime, timedelta, UTC
from flask import Blueprint, request, jsonify, url_for, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from app import db
from models import User
from models.roles import UserRole
from middleware.rbac import role_required
from utils import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
        
    try:
        existing_user = db.session.execute(
            db.select(User).filter_by(email=data['email'])
        ).scalar_one_or_none()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        role = None
        if 'role' in data:
            # Check if the role is valid
            if not UserRole.has_value(data['role']):
                return jsonify({'error': 'Invalid role'}), 400
                
            # Try to get auth token info without @jwt_required
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Authentication required to assign roles'}), 401
                
            # Verify token and get user identity
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                if not current_user_id:
                    return jsonify({'error': 'Authentication required to assign roles'}), 401
                    
                current_user = db.session.get(User, current_user_id)
                if not current_user:
                    return jsonify({'error': 'User not found'}), 404
                if not current_user.is_admin():
                    return jsonify({'error': 'Not authorized to assign roles'}), 403
                
                role = data['role']
            except Exception as jwt_error:
                return jsonify({
                    'error': 'Authentication failed',
                    'details': str(jwt_error),
                    'type': type(jwt_error).__name__
                }), 401
        
        # Create new user with role (will default to CANDIDATE if role is None)
        new_user = User(
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Debug log
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token."""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = db.session.execute(
            db.select(User).filter_by(email=data['email'])
        ).scalar_one_or_none()
        
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
            return jsonify({
                'error': 'Token generation failed',
                'details': str(e),
                'type': type(e).__name__
            }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to process login',
            'details': str(e),
            'type': type(e).__name__
        }), 500

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
    try:
        user = db.session.execute(
            db.select(User).filter_by(verification_token=token)
        ).scalar_one_or_none()
    
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400
            
        if user.verify_email(token):
            db.session.commit()
            return jsonify({'message': 'Email verified successfully'}), 200
        return jsonify({'error': 'Invalid or expired token'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to verify email',
            'details': str(e),
            'type': type(e).__name__
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
            
        user = db.session.execute(
            db.select(User).filter_by(email=data['email'])
        ).scalar_one_or_none()
        
        if not user:
            # Return 200 even if user not found for security
            return jsonify({'message': 'If the email exists, you will receive a reset link'}), 200
            
        token = user.generate_reset_token()
        db.session.flush()  # Flush changes before sending email
        
        reset_url = f"{request.host_url.rstrip('/')}/reset-password/{token}"
        if send_password_reset_email(user, reset_url):
            db.session.commit()
            return jsonify({'message': 'Password reset instructions sent'}), 200
        else:
            db.session.rollback()
            return jsonify({'error': 'Failed to send reset email'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to process password reset request',
            'details': str(e),
            'type': type(e).__name__
        }), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password with token."""
    try:
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({'error': 'New password is required'}), 400
            
        user = db.session.execute(
            db.select(User).filter_by(reset_token=token)
        ).scalar_one_or_none()
        
        if not user or not user.verify_reset_token(token):
            return jsonify({'error': 'Invalid or expired reset token'}), 400
            
        user.set_password(data['password'])
        user.reset_token = None
        user.reset_token_expires = None
        
        try:
            db.session.commit()
            return jsonify({'message': 'Password reset successful'}), 200
        except Exception as commit_error:
            db.session.rollback()
            return jsonify({
                'error': 'Failed to save password',
                'details': str(commit_error),
                'type': type(commit_error).__name__
            }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to process password reset',
            'details': str(e),
            'type': type(e).__name__
        }), 500

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

@auth_bp.route('/roles', methods=['GET'])
@jwt_required()
def list_roles():
    """List all available roles. Any authenticated user can access this."""
    roles = [{'name': role.name, 'value': role.value} for role in UserRole]
    return jsonify({'roles': roles})

@auth_bp.route('/roles/admin', methods=['GET'])
@jwt_required()
@role_required(UserRole.ADMIN)
def admin_list_roles():
    """Admin route for listing roles. Only admins can access this."""
    roles = [{'name': role.name, 'value': role.value} for role in UserRole]
    return jsonify({'roles': roles})

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@role_required(UserRole.ADMIN)
def update_user_role(user_id):
    """Update a user's role. Only admins can perform this action."""
    try:
        data = request.get_json()
        
        if not data or 'role' not in data:
            return jsonify({'error': 'Role is required'}), 400
            
        new_role = data['role']
        if not UserRole.has_value(new_role):
            return jsonify({'error': 'Invalid role'}), 400
            
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        user.set_role(new_role)  # Use the set_role method to validate and set the role
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        })
    except ValueError as ve:
        db.session.rollback()
        return jsonify({
            'error': 'Invalid role value',
            'details': str(ve),
            'type': 'ValueError'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update user role',
            'details': str(e),
            'type': type(e).__name__
        }), 500

@auth_bp.route('/users/roles', methods=['GET'])
@jwt_required()
@role_required(UserRole.ADMIN, UserRole.TALENT_LEAD)
def list_users_by_role():
    """List users filtered by role. Only admins and talent leads can access this."""
    try:
        role = request.args.get('role')
        if role and not UserRole.has_value(role):
            return jsonify({'error': 'Invalid role'}), 400
            
        query = db.select(User)
        if role:
            query = query.filter_by(role=role)
            
        users = db.session.execute(query).scalars().all()
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to list users by role',
            'details': str(e),
            'type': type(e).__name__
        }), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required(UserRole.ADMIN, UserRole.TALENT_LEAD)
def list_users():
    """List all users. Admins can see all users, Talent Leads can only see Candidates."""
    try:
        current_user_id = get_jwt_identity()
        current_user = db.session.get(User, current_user_id)
        
        if current_user is None:
            return jsonify({'error': 'User not found'}), 404
            
        if current_user.is_admin():
            users = db.session.query(User).all()
        else:  # Talent Lead
            users = db.session.query(User).filter_by(role=UserRole.CANDIDATE.value).all()
            
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to list users', 'details': str(e)}), 500
