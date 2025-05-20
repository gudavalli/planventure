# filepath: c:\Users\sreen\learning\copilot-agent\planventure\planventure-account\tests\conftest.py
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
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use in-memory SQLite for tests
        'JWT_SECRET_KEY': 'this-is-a-test-key',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_ERROR_MESSAGE_KEY': 'message',
        'JWT_HEADER_TYPE': 'Bearer',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'PROPAGATE_EXCEPTIONS': True
    })

    # Push an app context and create tables
    ctx = app.app_context()
    ctx.push()

    # Initialize database
    db.create_all()

    yield app

    # Clean up resources
    try:
        db.session.rollback()  # Roll back any active transactions
        db.session.remove()  # Remove session
        db.drop_all()  # Drop all tables
    finally:
        ctx.pop()  # Always pop the context

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
    # Create user and add to database
    user = User(
        email='test@example.com',
        password='password123',
        first_name='Test',
        last_name='User'
    )
    user.is_active = True
    user.is_verified = True
    user.verification_token = 'test-verification-token'
    user.verification_token_expires = datetime.now(UTC) + timedelta(hours=1)
    user.reset_token = 'test-reset-token'
    user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
    
    db.session.add(user)
    db.session.commit()

    yield user

    # Clean up
    try:
        db.session.rollback()  # Roll back any active transaction
        db.session.query(User).filter_by(email='test@example.com').delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise

@pytest.fixture
def test_user_with_expired_token(app):
    """Create a test user with expired verification and reset tokens."""
    # Create user and add to database
    user = User(
        email='expired@example.com',
        password='password123',
        first_name='Test',
        last_name='User'
    )
    user.is_active = True
    user.is_verified = True
    user.verification_token = 'expired-verification-token'
    user.verification_token_expires = datetime.now(UTC) - timedelta(hours=1)
    user.reset_token = 'expired-reset-token'
    user.reset_token_expires = datetime.now(UTC) - timedelta(hours=1)
    
    db.session.add(user)
    db.session.commit()
    
    yield user

    # Clean up
    try:
        db.session.rollback()  # Roll back any active transaction
        db.session.query(User).filter_by(email='expired@example.com').delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise
