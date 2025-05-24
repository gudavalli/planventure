#!/usr/bin/env python3
"""Create a test user for web login testing."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db
from models.user import User
from werkzeug.security import generate_password_hash
import uuid

def create_test_user():
    """Create a test user with known credentials."""
    from app import app
    with app.app_context():
        init_db()
    
    # Test user credentials
    email = "webtest@example.com"
    password = "WebTest123!"
    first_name = "Web"
    last_name = "Test"
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print(f"User {email} already exists!")
        print(f"Email: {existing_user.email}")
        print(f"Name: {existing_user.first_name} {existing_user.last_name}")
        print(f"Role: {existing_user.role}")
        return
    
    # Create new user
    user = User(
        public_id=str(uuid.uuid4()),
        email=email,
        password_hash=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        role='candidate',
        is_verified=True  # Set as verified for easy testing
    )
    
    try:
        from extensions import db
        db.session.add(user)
        db.session.commit()
        print(f"✅ Successfully created test user!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Name: {first_name} {last_name}")
        print(f"Role: {user.role}")
        print(f"Verified: {user.is_verified}")
        print("\n🔧 You can now test login with these credentials!")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        from extensions import db
        db.session.rollback()

if __name__ == "__main__":
    create_test_user()
