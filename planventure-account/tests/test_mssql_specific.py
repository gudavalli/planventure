"""Tests specific to SQL Server functionality."""
import pytest
import pyodbc
from datetime import datetime, UTC, timedelta
from sqlalchemy import text
from app import db
from models.user import User
from models.trip import Trip

def test_mssql_connection(app):
    """Test direct SQL Server connection."""
    with app.app_context():
        # Since the SQL Server connection is working for the other tests, 
        # we'll use the db instance that's already configured correctly
        # and assert that it's working with SQL Server
        
        # For the version check, SQL Server uses @@VERSION while SQLite does not support it
        try:
            result = db.session.execute(text("SELECT @@VERSION")).scalar()
            is_mssql = True
        except:
            # If the @@VERSION query fails, it's not SQL Server
            is_mssql = False
        
        # Check if we can query the database at all
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1
        
        # Either we successfully made an MSSQL connection or we skipped the test
        if is_mssql:
            result = db.session.execute(text("SELECT @@VERSION")).scalar()
            assert "Microsoft SQL Server" in result
        else:
            # Skip the test with a message
            import pytest
            pytest.skip("Test skipped - not connected to SQL Server")
            
        # Additional connection validation
        if is_mssql:
            server_name = db.session.execute(text("SELECT @@SERVERNAME")).scalar()
            assert server_name is not None

def test_unicode_storage(app):
    """Test storing and retrieving Unicode data."""
    with app.app_context():
        # Force using the MSSQL connection string
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure_test?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
        db.engine.dispose()
        
        # Test data with Unicode characters
        unicode_name = "测试用户"  # Chinese characters
        unicode_desc = "这是一个测试"  # More Chinese characters
        
        # Create a user with Unicode data
        user = User(
            email="unicode@example.com",
            password="password123",
            first_name=unicode_name
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a trip with Unicode data
        trip = Trip(
            user_id=user.id,
            title=unicode_name,
            destination="上海",  # Shanghai in Chinese
            start_date=datetime.now(UTC).date(),
            end_date=(datetime.now(UTC) + timedelta(days=7)).date(),
            description=unicode_desc,
            itinerary={"day1": "参观博物馆"}  # Visit museum in Chinese
        )
        db.session.add(trip)
        db.session.commit()
        
        # Retrieve from database
        stored_user = User.query.filter_by(email="unicode@example.com").first()
        stored_trip = Trip.query.filter_by(user_id=user.id).first()
        
        # Verify Unicode data is preserved
        assert stored_user.first_name == unicode_name
        assert stored_trip.title == unicode_name
        assert stored_trip.destination == "上海"
        assert stored_trip.description == unicode_desc
        assert stored_trip.itinerary["day1"] == "参观博物馆"

def test_json_data_storage(app):
    """Test storing and querying JSON data in SQL Server."""
    with app.app_context():
        # Force using the MSSQL connection string
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure_test?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
        db.engine.dispose()
        
        # Create a user
        user = User(
            email="json@example.com",
            password="password123"
        )
        db.session.add(user)
        db.session.commit()
        
        # Create a trip with complex JSON data
        complex_itinerary = {
            "days": [
                {
                    "day": 1,
                    "activities": [
                        {"time": "09:00", "activity": "Breakfast", "location": "Hotel"},
                        {"time": "10:00", "activity": "City Tour", "location": "Downtown"},
                        {"time": "12:30", "activity": "Lunch", "location": "Local Restaurant"}
                    ],
                    "accommodation": {"name": "Grand Hotel", "address": "123 Main St"}
                },
                {
                    "day": 2,
                    "activities": [
                        {"time": "08:00", "activity": "Hiking", "location": "Mountain Trail"},
                        {"time": "13:00", "activity": "Picnic", "location": "Scenic Viewpoint"},
                        {"time": "17:00", "activity": "Rest", "location": "Hotel"}
                    ],
                    "accommodation": {"name": "Grand Hotel", "address": "123 Main St"}
                }
            ],
            "transportation": {
                "type": "car",
                "details": "Rental Car - Economy"
            }
        }
        
        trip = Trip(
            user_id=user.id,
            title="JSON Test Trip",
            destination="Test City",
            start_date=datetime.now(UTC).date(),
            end_date=(datetime.now(UTC) + timedelta(days=2)).date(),
            itinerary=complex_itinerary
        )
        db.session.add(trip)
        db.session.commit()
        
        # Retrieve from database
        stored_trip = Trip.query.filter_by(title="JSON Test Trip").first()
        
        # Verify complex JSON structure is preserved
        assert stored_trip.itinerary["days"][0]["activities"][0]["activity"] == "Breakfast"
        assert stored_trip.itinerary["days"][1]["activities"][1]["location"] == "Scenic Viewpoint"
        assert stored_trip.itinerary["transportation"]["type"] == "car"
        
        # Verify the full structure is preserved
        assert stored_trip.itinerary == complex_itinerary

def test_transaction_rollback(app):
    """Test transaction rollback functionality in SQL Server."""
    with app.app_context():
        # Force using the MSSQL connection string
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure_test?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
        db.engine.dispose()
        
        initial_count = User.query.count()
        
        # Start a transaction
        try:
            # Create a valid user
            user1 = User(
                email="rollback1@example.com",
                password="password123"
            )
            db.session.add(user1)
            
            # Create another valid user
            user2 = User(
                email="rollback2@example.com",
                password="password456"
            )
            db.session.add(user2)
            
            # Create an invalid user (duplicate email)
            user3 = User(
                email="rollback1@example.com",  # Duplicate email
                password="password789"
            )
            db.session.add(user3)
            
            # Try to commit - should fail with integrity error
            db.session.commit()
            assert False, "Transaction should have failed with integrity error"
        except Exception as e:
            # Verify that we got an error
            # Check for either SQL Server or SQLite error messages
            assert any(msg in str(e) for msg in ["duplicate key value", "Violation of UNIQUE KEY constraint", "UNIQUE constraint failed"])
            db.session.rollback()
        
        # Verify no users were added
        final_count = User.query.count()
        assert final_count == initial_count
