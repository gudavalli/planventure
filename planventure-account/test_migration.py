#!/usr/bin/env python
"""Script to validate the PlanVenture Account Service migration from SQLite to SQL Server."""
import os
import sys
import json
import sqlite3
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
from app import create_app, db
from models.user import User
from models.trip import Trip

# Load environment variables
load_dotenv()

def validate_migration():
    """Validate the migration from SQLite to SQL Server."""
    print("PlanVenture Account Service Migration Validation")
    print("====================================\n")
    
    # Check if SQLite database exists
    if not os.path.exists('instance/planventure.db'):
        print("ERROR: SQLite database not found. Cannot validate migration.")
        print("Please ensure the SQLite database is available for comparison.")
        return False
    
    # Connect to SQLite database
    print("Connecting to SQLite database...")
    try:
        sqlite_conn = sqlite3.connect('instance/planventure.db')
        sqlite_conn.row_factory = sqlite3.Row
        print("Connected successfully to SQLite database.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQLite database: {str(e)}")
        return False
    
    # Connect to SQL Server
    server = os.getenv('DB_SERVER', 'localhost,1433')
    username = os.getenv('DB_USERNAME', 'sa')
    password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
    database = os.getenv('DB_NAME', 'planventure')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    print(f"Connecting to SQL Server at {server}...")
    try:
        mssql_conn = pyodbc.connect(conn_str)
        print("Connected successfully to SQL Server.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQL Server: {str(e)}")
        return False
    
    # Create Flask app context to use models
    app = create_app()
    
    with app.app_context():
        # Step 1: Count records in both databases to compare
        try:
            print("\nStep 1: Comparing record counts...")
            
            # Check users
            sqlite_cursor = sqlite_conn.cursor()
            mssql_cursor = mssql_conn.cursor()
            
            # Try to find the correct table names - adapt if your SQLite table names differ
            try:
                sqlite_cursor.execute("SELECT COUNT(*) FROM users")
            except sqlite3.OperationalError:
                # Fallback to 'user' if 'users' doesn't exist
                sqlite_cursor.execute("SELECT COUNT(*) FROM user")
            
            sqlite_user_count = sqlite_cursor.fetchone()[0]
            
            mssql_cursor.execute("SELECT COUNT(*) FROM users")
            mssql_user_count = mssql_cursor.fetchone()[0]
            
            print(f"Users: SQLite={sqlite_user_count}, SQL Server={mssql_user_count}")
            
            # Check trips
            try:
                sqlite_cursor.execute("SELECT COUNT(*) FROM trips")
            except sqlite3.OperationalError:
                # Fallback to 'trip' if 'trips' doesn't exist
                try:
                    sqlite_cursor.execute("SELECT COUNT(*) FROM trip")
                except sqlite3.OperationalError:
                    print("WARNING: Could not find trips table in SQLite database.")
                    sqlite_trip_count = 0
                else:
                    sqlite_trip_count = sqlite_cursor.fetchone()[0]
            else:
                sqlite_trip_count = sqlite_cursor.fetchone()[0]
            
            try:
                mssql_cursor.execute("SELECT COUNT(*) FROM trips")
                mssql_trip_count = mssql_cursor.fetchone()[0]
                print(f"Trips: SQLite={sqlite_trip_count}, SQL Server={mssql_trip_count}")
            except:
                print("WARNING: Could not find trips table in SQL Server database.")
                
            if sqlite_user_count != mssql_user_count:
                print("WARNING: User count mismatch between databases!")
            else:
                print("SUCCESS: User count matches between databases.")
                
            if sqlite_trip_count and sqlite_trip_count != mssql_trip_count:
                print("WARNING: Trip count mismatch between databases!")
            elif sqlite_trip_count:
                print("SUCCESS: Trip count matches between databases.")
                
        except Exception as e:
            print(f"ERROR: Failed to compare record counts: {str(e)}")
            
        # Step 2: Sample data validation
        print("\nStep 2: Validating sample data...")
        
        try:
            # Check a sample user
            sqlite_cursor.execute("SELECT email FROM users LIMIT 1")
            result = sqlite_cursor.fetchone()
            if not result:
                # Try the other table name
                sqlite_cursor.execute("SELECT email FROM user LIMIT 1")
                result = sqlite_cursor.fetchone()
                
            if result:
                sample_email = result[0]
                print(f"Checking user with email: {sample_email}")
                
                # Check in SQL Server
                mssql_cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (sample_email,))
                count = mssql_cursor.fetchone()[0]
                
                if count > 0:
                    print(f"SUCCESS: Found user {sample_email} in SQL Server database.")
                else:
                    print(f"WARNING: User {sample_email} not found in SQL Server database.")
            else:
                print("No users found in SQLite database for comparison.")
                
        except Exception as e:
            print(f"ERROR: Failed to validate sample data: {str(e)}")
            
        # Step 3: Test database functionality
        print("\nStep 3: Testing database functionality...")
        
        try:
            # Test user query
            users = User.query.all()
            print(f"Retrieved {len(users)} users from SQL Server using SQLAlchemy ORM.")
            
            # Test trip query if the model exists
            trips = Trip.query.all()
            print(f"Retrieved {len(trips)} trips from SQL Server using SQLAlchemy ORM.")
            
            # Try a more complex query
            if len(users) > 0:
                user_id = users[0].id
                user_trips = Trip.query.filter_by(user_id=user_id).all()
                print(f"Retrieved {len(user_trips)} trips for user ID {user_id}.")
                
        except Exception as e:
            print(f"ERROR: Failed to test database functionality: {str(e)}")
        
        # Step 4: Performance test (simple)
        print("\nStep 4: Running simple performance test...")
        
        try:
            start_time = datetime.now()
            all_users_with_trips = db.session.query(User).join(Trip).all()
            duration = (datetime.now() - start_time).total_seconds()
            print(f"Retrieved {len(all_users_with_trips)} users with trips in {duration:.4f} seconds.")
            
        except Exception as e:
            print(f"ERROR: Failed to run performance test: {str(e)}")
            
    # Close connections
    sqlite_conn.close()
    mssql_conn.close()
    
    print("\nMigration validation completed.")
    return True

if __name__ == '__main__':
    validate_migration()
