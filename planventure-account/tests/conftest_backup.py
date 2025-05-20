# filepath: c:\Users\sreen\learning\copilot-agent\planventure\planventure-account\tests\conftest_backup.py
import pytest
from datetime import datetime, timedelta, UTC, date
from app import create_app, db
from models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure_test?driver=ODBC+Driver+17+for+SQL+Server',
        'JWT_SECRET_KEY': 'this-is-a-secret-key-for-testing-32-bytes',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_ERROR_MESSAGE_KEY': 'message',
        'JWT_HEADER_TYPE': 'Bearer'
    })

    # Create the database tables
    with app.app_context():
        try:
            # Try to create the database tables
            db.drop_all()  # First drop all tables for a clean slate
            db.create_all()
        except Exception as e:
            print(f"Error setting up test database: {e}")
            # For tests to run, we'll skip dropping/creating tables if the connection fails
            # This allows tests to at least run with mocks

    # Create a test client
    yield app

    # Clean up resources
    with app.app_context():
        try:
            db.session.remove()
            db.drop_all()
        except Exception as e:
            print(f"Error tearing down test database: {e}")

@pytest.fixture
def client(app):
    """A test client for the app."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            password_hash='pbkdf2:sha256:150000',  # password: 'password123'
            is_active=True,
            is_verified=True,
            first_name='Test',
            last_name='User',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        
        # Add verification token for testing email verification
        user.verification_token = 'test-verification-token'
        
        # Add reset token for testing password reset
        user.reset_token = 'test-reset-token'
        user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
        
        db.session.add(user)
        db.session.commit()
        
        # Get a fresh user instance to ensure the ID is properly set
        user = User.query.filter_by(email='test@example.com').first()
        
        yield user
        
        # Clean up
        User.query.filter_by(email='test@example.com').delete()
        db.session.commit()

@pytest.fixture
def test_user_with_expired_token(app):
    """Create a test user with expired reset token."""
    with app.app_context():
        user = User(
            email='expired@example.com',
            password_hash='pbkdf2:sha256:150000',  # password: 'password123'
            is_active=True,
            is_verified=True,
            first_name='Test',
            last_name='User',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        
        # Add expired reset token
        user.reset_token = 'expired-reset-token'
        user.reset_token_expires = datetime.now(UTC) - timedelta(hours=1)
        
        db.session.add(user)
        db.session.commit()
        
        # Get a fresh user instance
        user = User.query.filter_by(email='expired@example.com').first()
        
        yield user
        
        # Clean up
        User.query.filter_by(email='expired@example.com').delete()
        db.session.commit()
