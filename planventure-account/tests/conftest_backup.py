import pytest
from datetime import datetime, timedelta, UTC, date
from app import create_app, db
from models.user import User
from models.trip import Trip

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
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_TYPE': 'Bearer',
        'JWT_ALGORITHM': 'HS256',
        'JWT_IDENTITY_CLAIM': 'sub'
    })

    # Create the database and the database tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up database before each test."""
    with app.app_context():
        # Clean up all tables
        db.drop_all()
        db.create_all()
        yield

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
        user.verification_token_expires = datetime.now(UTC) + timedelta(hours=24)        db.session.add(user)
        db.session.commit()
        
        # Get a fresh user instance to ensure the ID is properly set
        fresh_user = db.session.get(User, user.id)
        assert fresh_user is not None
        assert fresh_user.id is not None
        return fresh_user
        
@pytest.fixture
def test_trip(test_user, app):
    """Create a test trip."""
    with app.app_context():
        # Create a test trip for the test user
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            destination="Test Destination",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
            description="A test trip created for testing",
            latitude="40.7128",
            longitude="-74.0060",
            itinerary={
                "day1": "Arrive and check in",
                "day2": "Explore the city",
                "day3": "Visit museums"
            }
        )
        db.session.add(trip)
        db.session.commit()
        
        # Get a fresh trip instance to ensure the ID is properly set
        fresh_trip = db.session.get(Trip, trip.id)
        assert fresh_trip is not None
        assert fresh_trip.id is not None
        return fresh_trip