#!/usr/bin/env python
"""Script to validate the database schema after migration."""
import os
import sys
import pyodbc
from dotenv import load_dotenv
from app import create_app, db
from models.user import User
from models.database import get_connection_string

# Load environment variables
load_dotenv()

def get_table_schema(cursor, table_name):
    """Get column information for a table."""
    try:
        cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE " +
                       f"FROM INFORMATION_SCHEMA.COLUMNS " +
                       f"WHERE TABLE_NAME = '{table_name}' " +
                       f"ORDER BY ORDINAL_POSITION")
        return cursor.fetchall()
    except Exception as e:
        print(f"ERROR: Could not get schema for {table_name}: {str(e)}")
        return []

def validate_schema():
    """Validate the database schema after migration."""
    print("PlanVenture Account Service Schema Validation")
    print("===================================\n")
    
    # Connect to SQL Server
    try:
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected successfully to SQL Server.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQL Server: {str(e)}")
        return False
    
    try:
        # Step 1: Verify database exists
        print("\nStep 1: Verifying database exists...")
        cursor.execute("SELECT DB_NAME()")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")
        
        # Step 2: Check if expected tables exist
        print("\nStep 2: Checking expected tables...")
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("Found tables:")
        for table in tables:
            print(f"  - {table}")
            
        expected_tables = ['users']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print("\nWARNING: The following expected tables are missing:")
            for table in missing_tables:
                print(f"  - {table}")
        else:
            print("\nAll expected tables are present.")
        
        # Step 3: Validate User table schema
        print("\nStep 3: Validating User model schema...")
        user_schema = get_table_schema(cursor, 'users')
        print("User table columns:")
        for column in user_schema:
            col_name, data_type, max_length, nullable = column
            max_length_str = f"({max_length})" if max_length else ""
            nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"  - {col_name}: {data_type}{max_length_str} {nullable_str}")
            
        # Check if important columns exist
        user_columns = [col[0].lower() for col in user_schema]
        required_user_columns = ['id', 'email', 'password_hash', 'is_active', 'is_verified']
        missing_columns = [col for col in required_user_columns if col.lower() not in user_columns]
        
        if missing_columns:
            print("\nWARNING: Missing required columns in users table:")
            for col in missing_columns:
                print(f"  - {col}")
        else:
            print("\nAll required user columns are present.")
        
        # Step 4: Test database queries
        print("\nStep 4: Testing database queries...")
        
        # Create Flask app context to use models
        app = create_app()
        
        with app.app_context():
            # Test User model
            try:
                user_count = User.query.count()
                print(f"User model query successful. Found {user_count} users.")
            except Exception as e:
                print(f"ERROR: User model query failed: {str(e)}")
                
        print("\nSchema validation completed.")
        return len(missing_tables) == 0 and len(missing_columns) == 0
        
    except Exception as e:
        print(f"ERROR during schema validation: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = validate_schema()
    sys.exit(0 if success else 1)
