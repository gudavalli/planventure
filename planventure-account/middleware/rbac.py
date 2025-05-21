"""Role-based access control middleware."""
from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.roles import UserRole
from models import User
from extensions import db

def role_required(*required_roles):
    """Decorator to check if user has any of the required roles.
    
    Args:
        required_roles: Variable number of role values from UserRole enum
    """
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            # First verify the token
            verify_jwt_in_request()
            
            # Get the current user
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Get user from database without explicit transaction
            try:
                user = db.session.get(User, int(user_id))
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                g.user = user
                
                # Convert required_roles to values if they are enum members
                role_values = [r.value if isinstance(r, UserRole) else r for r in required_roles]
                
                # If no roles specified, allow access
                if not role_values:
                    return fn(*args, **kwargs)
                
                # Admin can access everything
                if user.role == UserRole.ADMIN.value:
                    return fn(*args, **kwargs)
                
                # Check if user has any of the required roles
                if user.role in role_values:
                    return fn(*args, **kwargs)
                
                return jsonify({'error': 'Insufficient permissions'}), 403
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
                
        return decorated_function
    return decorator
