"""Database initialization script for PlanVenture API."""
import os
import pyodbc
import argparse
from dotenv import load_dotenv
from flask import Flask
from app import create_app, db
from models.database import create_database_if_not_exists

# Load environment variables from .env file
load_dotenv()

def init_database(database_name='planventure', create_test_db=True):
    """Initialize the database schema.
    
    Args:
        database_name (str): The name of the database to create/initialize
        create_test_db (bool): Whether to create a test database as well
    """
    try:
        # Get database config from environment
        server = os.getenv('DB_SERVER', 'localhost,1433')
        username = os.getenv('DB_USERNAME', 'sa')
        password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        print(f"Creating database '{database_name}' if it doesn't exist...")
        
        # Create the main database
        if not create_database_if_not_exists(database_name):
            print("Failed to create database. Check your SQL Server connection.")
            return False
        
        # Create test database if requested
        if create_test_db:
            test_db_name = f"{database_name}_test"
            print(f"Creating test database '{test_db_name}' if it doesn't exist...")
            if not create_database_if_not_exists(test_db_name):
                print("Failed to create test database, but continuing...")
        
        # Create tables using SQLAlchemy
        print("Creating tables using SQLAlchemy...")
        app = create_app()
        with app.app_context():
            try:
                db.create_all()
                print(f"Tables created successfully in the '{database_name}' database.")
                return True
            except Exception as e:
                print(f"Error creating tables: {str(e)}")
                return False
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def main():
    """Command-line interface for database initialization."""
    parser = argparse.ArgumentParser(description='Initialize the PlanVenture database.')
    parser.add_argument('--no-test-db', action='store_true', help='Skip creating test database')
    parser.add_argument('--db-name', type=str, default='planventure', help='Database name')
    
    args = parser.parse_args()
    
    success = init_database(
        database_name=args.db_name, 
        create_test_db=not args.no_test_db
    )
    
    if success:
        print("Database initialization completed successfully.")
    else:
        print("Database initialization encountered errors. Check the output above.")
        exit(1)

if __name__ == "__main__":
    main()
