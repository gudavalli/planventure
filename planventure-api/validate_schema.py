#!/usr/bin/env python
"""Script to validate the database schema after migration to SQL Server."""
import os
import sys
import pyodbc
from dotenv import load_dotenv
from app import create_app, db
from sqlalchemy import inspect, text
from models.user import User
from models.trip import Trip

# Load environment variables
load_dotenv()

def get_table_schema(cursor, table_name):
    """Get the schema of a table."""
    cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION")
    return cursor.fetchall()

def validate_schema():
    """Validate the database schema after migration."""
    print("PlanVenture API Schema Validation")
    print("=================================\n")
    
    # Get database config from environment
    server = os.getenv('DB_SERVER', 'localhost,1433')
    username = os.getenv('DB_USERNAME', 'sa')
    password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
    database = os.getenv('DB_NAME', 'planventure')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        # Connect directly with pyodbc
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected successfully to SQL Server.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQL Server: {str(e)}")
        return False
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get SQLAlchemy inspector
        inspector = inspect(db.engine)
        
        # Check all tables
        print("\nChecking database tables...")
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        expected_tables = ['users', 'trips']
        for table in expected_tables:
            if table in tables:
                print(f"✓ Table '{table}' exists")
            else:
                print(f"✗ Table '{table}' is missing!")
        
        # Check columns for each model
        print("\nValidating User model schema...")
        user_schema = get_table_schema(cursor, 'users')
        print("User table columns:")
        for column in user_schema:
            print(f"  - {column.COLUMN_NAME}: {column.DATA_TYPE}", end="")
            if column.CHARACTER_MAXIMUM_LENGTH:
                if column.CHARACTER_MAXIMUM_LENGTH == -1:
                    print(f"(MAX)", end="")
                else:
                    print(f"({column.CHARACTER_MAXIMUM_LENGTH})", end="")
            print(f" {'NULL' if column.IS_NULLABLE == 'YES' else 'NOT NULL'}")
        
        print("\nValidating Trip model schema...")
        trip_schema = get_table_schema(cursor, 'trips')
        print("Trip table columns:")
        for column in trip_schema:
            print(f"  - {column.COLUMN_NAME}: {column.DATA_TYPE}", end="")
            if column.CHARACTER_MAXIMUM_LENGTH:
                if column.CHARACTER_MAXIMUM_LENGTH == -1:
                    print(f"(MAX)", end="")
                else:
                    print(f"({column.CHARACTER_MAXIMUM_LENGTH})", end="")
            print(f" {'NULL' if column.IS_NULLABLE == 'YES' else 'NOT NULL'}")
        
        # Check indexes
        print("\nValidating indexes...")
        for table in expected_tables:
            indexes = inspector.get_indexes(table)
            foreign_keys = inspector.get_foreign_keys(table)
            
            print(f"\nIndexes for '{table}':")
            for index in indexes:
                print(f"  - {index['name']}: columns={', '.join(index['column_names'])} (unique={index['unique']})")
            
            print(f"Foreign keys for '{table}':")
            for fk in foreign_keys:
                print(f"  - {fk['name']}: {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
        
        # Run test queries
        print("\nRunning test queries...")
        
        # Test User model
        try:
            user_count = User.query.count()
            print(f"User model query successful. Found {user_count} users.")
        except Exception as e:
            print(f"ERROR: User model query failed: {str(e)}")
        
        # Test Trip model
        try:
            trip_count = Trip.query.count()
            print(f"Trip model query successful. Found {trip_count} trips.")
        except Exception as e:
            print(f"ERROR: Trip model query failed: {str(e)}")
        
        # Test a join query
        try:
            result = db.session.query(User, Trip).join(Trip, Trip.user_id == User.id).count()
            print(f"Join query successful. Found {result} user-trip associations.")
        except Exception as e:
            print(f"ERROR: Join query failed: {str(e)}")
        
        # Execute a query to test collation
        print("\nTesting string collation (case sensitivity)...")
        try:
            # Create a test user with mixed case if none exist
            if User.query.count() == 0:
                test_user = User(email="Test@Example.com", password="password123")
                db.session.add(test_user)
                db.session.commit()
                print("Created test user for collation test")
            
            # Test case insensitive search
            result1 = User.query.filter(User.email.ilike("test@example.com")).count()
            result2 = User.query.filter(User.email == "test@example.com").count()
            print(f"Case insensitive search (ILIKE): found {result1} results")
            print(f"Case sensitive search (=): found {result2} results")
        except Exception as e:
            print(f"ERROR: Collation test failed: {str(e)}")
    
    # Close connection
    conn.close()
    
    print("\nSchema validation completed.")
    return True

if __name__ == '__main__':
    validate_schema()
