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

# Load environment variables
load_dotenv()

def validate_migration():
    """Validate the migration from SQLite to SQL Server."""
    print("PlanVenture Account Service Migration Validation")
    print("====================================\n")
    
    # Get SQLite path
    app = create_app()
    sqlite_path = app.config.get("SQLALCHEMY_DATABASE_URI").replace("sqlite:///", "")
    
    if not os.path.exists(sqlite_path):
        print(f"ERROR: SQLite database not found at {sqlite_path}")
        return False
        
    print(f"Using SQLite database: {sqlite_path}")
    
    try:
        sqlite_conn = sqlite3.connect(sqlite_path)
        print("Connected successfully to SQLite database.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQLite database: {str(e)}")
        return False
    
    # Get SQL Server connection details from environment
    server = os.getenv("DB_SERVER", "localhost")
    username = os.getenv("DB_USERNAME", "sa")
    password = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")
    database = os.getenv("DB_NAME", "planventure")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    
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
                # Fallback to "user" if "users" doesn"t exist
                sqlite_cursor.execute("SELECT COUNT(*) FROM user")
            
            sqlite_user_count = sqlite_cursor.fetchone()[0]
            
            mssql_cursor.execute("SELECT COUNT(*) FROM users")
            mssql_user_count = mssql_cursor.fetchone()[0]
            
            print(f"Users: SQLite={sqlite_user_count}, SQL Server={mssql_user_count}")
                
            if sqlite_user_count != mssql_user_count:
                print("WARNING: User count mismatch between databases!")
            else:
                print("SUCCESS: User count matches between databases.")
                
        except Exception as e:
            print(f"ERROR: Failed to compare record counts: {str(e)}")
            
        # Step 2: Sample data validation
        print("\nStep 2: Validating sample data...")
        
        try:
            # Check a sample user
            sqlite_cursor.execute("SELECT email FROM users LIMIT 1")
            result = sqlite_cursor.fetchone()
            if result:
                sample_email = result[0]
                
                mssql_cursor.execute(f"SELECT email FROM users WHERE email = ?", (sample_email,))
                result = mssql_cursor.fetchone()
                
                if result and result[0] == sample_email:
                    print(f"SUCCESS: Found matching user with email {sample_email}")
                else:
                    print(f"WARNING: Could not find matching user with email {sample_email}")
            else:
                print("WARNING: No sample users found in SQLite database")
                
            # Test ORM query
            print("\nStep 3: Testing ORM queries...")
            
            # Test User query
            start_time = datetime.now()
            users = User.query.all()
            query_time = (datetime.now() - start_time).total_seconds()
            
            print(f"User query returned {len(users)} records in {query_time:.3f} seconds")
            
            if users:
                print(f"Sample user: {users[0].email}")
            
        except Exception as e:
            print(f"ERROR during data validation: {str(e)}")
            
    # Step 4: Check database performance
    print("\nStep 4: Testing database performance...")
    
    try:
        # Basic performance test
        start_time = datetime.now()
        mssql_cursor.execute("SELECT TOP 100 * FROM users")
        rows = mssql_cursor.fetchall()
        query_time = (datetime.now() - start_time).total_seconds()
        
        print(f"Performance test: fetched {len(rows)} users in {query_time:.3f} seconds")
        
        # Check indexes
        mssql_cursor.execute("""
            SELECT i.name, o.name
            FROM sys.indexes i
            JOIN sys.objects o ON i.object_id = o.object_id
            WHERE o.type = "U"
            ORDER BY o.name, i.name
        """)
        
        print("\nSQL Server indexes:")
        indexes = mssql_cursor.fetchall()
        for idx in indexes:
            print(f"  - {idx[1]}: {idx[0]}")
            
    except Exception as e:
        print(f"ERROR during performance testing: {str(e)}")
        
    # Clean up
    sqlite_conn.close()
    mssql_conn.close()
    
    print("\nMigration validation completed!")
    return True
    
if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1)
