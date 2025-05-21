"""Tests specific to SQL Server functionality."""
import pytest
from datetime import datetime, UTC, timedelta
from app import db
from models.user import User

def test_mssql_connection():
    """Test specific MSSQL connection features."""
    pytest.skip("This test requires a MSSQL server")

def test_unicode_storage(app):
    """Test storing and querying Unicode data."""
    with app.app_context():
        # Generate some Unicode content with Chinese characters
        unicode_name = "李明"  # Chinese name (Li Ming)
        # Create a user with Unicode data
        user = User(
            email="unicode@example.com",
            password="password123",
            first_name=unicode_name
        )
        db.session.add(user)
        db.session.commit()

        # Query the user back
        retrieved_user = User.query.filter_by(email="unicode@example.com").first()
        assert retrieved_user.first_name == unicode_name

        # Clean up
        db.session.delete(retrieved_user)
        db.session.commit()

def test_transaction_rollback(app):
    """Test transaction rollback functionality."""
    with app.app_context():
        initial_count = User.query.count()

        # Start a transaction
        try:
            # Create a user
            user = User(
                email="rollback@example.com",
                password="password123"
            )
            db.session.add(user)
            db.session.flush()

            # Simulate an error that would trigger a rollback
            raise Exception("Simulated error")

        except Exception:
            db.session.rollback()

        # Verify that the rollback was successful
        final_count = User.query.count()
        assert final_count == initial_count
        assert User.query.filter_by(email="rollback@example.com").first() is None
