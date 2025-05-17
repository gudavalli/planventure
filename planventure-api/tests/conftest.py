import pytest
from datetime import datetime, timedelta, UTC
from app import create_app, db
from models.user import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
        'JWT_ERROR_MESSAGE_KEY': 'message',
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_TYPE': 'Bearer'
    })

    # Create the database and the database tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        # Clear any existing test user
        User.query.filter_by(email='test@example.com').delete()
        db.session.commit()

        user = User(
            email='test@example.com',
            password='password123'
        )
        user.verification_token = 'test-verification-token'
        user.verification_token_expires = datetime.now(UTC) + timedelta(hours=24)
        db.session.add(user)
        db.session.commit()
        
        # Get a fresh user instance to ensure the ID is properly set
        fresh_user = db.session.get(User, user.id)
        assert fresh_user is not None
        assert fresh_user.id is not None
        return fresh_user