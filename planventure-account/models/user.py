from datetime import datetime, timedelta, UTC
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from .roles import UserRole

class User(db.Model):
    """User model for authentication and user management."""
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # SQL Server recommendation: Use nvarchar for Unicode strings
    email = db.Column(db.Unicode(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Unicode(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.Unicode(20), nullable=False, default=UserRole.CANDIDATE.value)  # Default role is CANDIDATE

    # Profile fields
    first_name = db.Column(db.Unicode(50))
    last_name = db.Column(db.Unicode(50))
    phone = db.Column(db.String(20))

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Verification and reset tokens
    verification_token = db.Column(db.String(100), unique=True)
    verification_token_expires = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)

    def __init__(self, email, password, first_name=None, last_name=None, role=None):
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role if role and UserRole.has_value(role) else UserRole.CANDIDATE.value
        self.generate_verification_token()

    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        """Generate verification token for email verification."""
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.now(UTC)

    def verify_email(self, token):
        """Verify email with token."""
        now = datetime.now(UTC)
        token_expires = self.verification_token_expires.replace(tzinfo=UTC) if self.verification_token_expires else None
        
        if (token == self.verification_token and 
            token_expires and 
            token_expires > now):
            self.is_verified = True
            self.verification_token = None
            self.verification_token_expires = None
            return True
        return False

    def generate_reset_token(self):
        """Generate password reset token."""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify password reset token."""
        now = datetime.now(UTC)
        token_expires = self.reset_token_expires.replace(tzinfo=UTC) if self.reset_token_expires else None
        
        if (token == self.reset_token and
            token_expires and
            token_expires > now):
            return True
        return False

    def has_role(self, role):
        """Check if user has the specified role."""
        if isinstance(role, UserRole):
            role = role.value
        return self.role == role

    def is_admin(self):
        """Check if user is an admin."""
        return self.has_role(UserRole.ADMIN)

    def is_talent_lead(self):
        """Check if user is a talent lead."""
        return self.has_role(UserRole.TALENT_LEAD)

    def is_candidate(self):
        """Check if user is a candidate."""
        return self.has_role(UserRole.CANDIDATE)

    def set_role(self, role):
        """Set user's role."""
        if isinstance(role, UserRole):
            role = role.value
        if not UserRole.has_value(role):
            raise ValueError(f"Invalid role: {role}")
        self.role = role

    def get_access_token(self):
        """Generate an access token for this user."""
        from flask_jwt_extended import create_access_token
        return create_access_token(identity=str(self.id))

    def __repr__(self):
        """String representation of the User object."""
        return f'<User {self.email}>'

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
