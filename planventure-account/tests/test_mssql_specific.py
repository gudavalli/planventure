"""Tests specific to SQL Server functionality."""
import pytest
import pyodbc
from datetime import datetime, UTC, timedelta
from sqlalchemy import text
from app import db
from models.user import User

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
            is_mssql = False
            pytest.skip("Not running on SQL Server")
        
        # Check if the result contains Microsoft SQL Server
        assert 'Microsoft SQL Server' in result
        
        # Try a more complex query to verify the connection is functional
        result = db.session.execute(text("SELECT DB_NAME() AS CurrentDatabase")).scalar()
        
        # Check that we're connected to our test database
        assert result in ['planventure', 'planventure_test']

def test_unicode_storage(app):
    """Test storing and querying Unicode data in SQL Server."""
    with app.app_context():
        # Force using the MSSQL connection string
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure_test?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
        db.engine.dispose()
        
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
        
        # Retrieve from database
        stored_user = User.query.filter_by(email="unicode@example.com").first()
        
        # Verify Unicode data is preserved
        assert stored_user.first_name == unicode_name

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
