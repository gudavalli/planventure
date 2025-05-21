# filepath: c:\Users\sreen\learning\copilot-agent\planventure\planventure-account\tests\conftest.py
import pytest
from datetime import datetime, timedelta, UTC, date
from app import create_app, db, TestConfig
from models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(config_class=TestConfig)

    # Push an app context
    ctx = app.app_context()
    ctx.push()

    # Initialize database and create a session
    db.create_all()
    
    # Start a transaction
    db.session.begin_nested()  # Create a savepoint

    yield app

    # Clean up resources
    try:
        db.session.rollback()  # Roll back to savepoint
        db.session.execute("DELETE FROM users")  # Clean up any remaining records
        db.session.commit()
        db.session.remove()  # Remove session
        db.drop_all()  # Drop tables
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.session.rollback()
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
    db.session.flush()  # Flush to ensure the user has an ID
    
    # Get a fresh instance to prevent detachment issues
    user_id = user.id
    db.session.commit()
    fresh_user = db.session.get(User, user_id)

    yield fresh_user

    # Clean up
    try:
        db.session.query(User).filter_by(email='test@example.com').delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    user = User(
        email='admin@test.com',
        password='password123',
        role='admin'
    )
    db.session.add(user)
    db.session.flush()  # Flush to ensure the user has an ID
    
    # Get a fresh instance to prevent detachment issues
    user_id = user.id
    db.session.commit()
    fresh_user = db.session.get(User, user_id)

    yield fresh_user

    try:
        db.session.query(User).filter_by(email='admin@test.com').delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise

@pytest.fixture
def talent_lead_user(app):
    """Create a talent lead user for testing."""
    user = User(
        email='talent@example.com',
        password='talentpass123',
        role='talent_lead'
    )
    db.session.add(user)
    db.session.flush()  # Flush to ensure the user has an ID
    
    # Get a fresh instance to prevent detachment issues
    user_id = user.id
    db.session.commit()
    fresh_user = db.session.get(User, user_id)

    yield fresh_user

    try:
        db.session.query(User).filter_by(email='talent@example.com').delete()
        db.session.commit()
    except:
        db.session.rollback()
        raise

@pytest.fixture
def candidate_user(app):
    """Create a candidate user for testing."""
    user = User(
        email='candidate@example.com',
        password='candidatepass123',
        role='candidate'
    )
    db.session.add(user)
    db.session.flush()  # Flush to ensure the user has an ID
    
    # Get a fresh instance to prevent detachment issues
    user_id = user.id
    db.session.commit()
    fresh_user = db.session.get(User, user_id)

    yield fresh_user

    try:
        db.session.query(User).filter_by(email='candidate@example.com').delete()
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
