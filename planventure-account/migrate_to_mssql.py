"""Script to migrate data from SQLite to SQL Server."""
import os
import sqlite3
import json
import pyodbc
from datetime import datetime
from dotenv import load_dotenv
from app import create_app, db
from models.user import User

# Load environment variables
load_dotenv()

def migrate_from_sqlite():
    """Migrate data from SQLite to SQL Server."""
    # Check if SQLite database exists
    if not os.path.exists('instance/planventure.db'):
        print("SQLite database not found. Nothing to migrate.")
        return
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Initialize SQL Server database (create tables)
        db.create_all()
        
        # Get SQL Server connection details from app config
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'mssql' not in db_url:
            print("ERROR: Not configured to use SQL Server. Migration aborted.")
            return
        
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect('instance/planventure.db')
        sqlite_conn.row_factory = sqlite3.Row
        
        print("Connected to SQLite database.")
        
        # Get SQL Server connection info
        server = os.getenv('DB_SERVER', 'localhost')
        username = os.getenv('DB_USERNAME', 'sa')
        password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
        database = os.getenv('DB_NAME', 'planventure')
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        # Create SQL Server connection
        conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        
        try:
            mssql_conn = pyodbc.connect(conn_str)
            print("Connected to SQL Server database.")
        except Exception as e:
            print(f"ERROR: Could not connect to SQL Server: {str(e)}")
            sqlite_conn.close()
            return
        
        try:
            # Begin migration process
            print("\nBeginning migration process...")
            
            # Migrate users
            print("\nMigrating users...")
            users = sqlite_conn.execute('SELECT * FROM users').fetchall()
            
            if users:
                migrated_count = 0
                
                for user in users:
                    # Convert SQLite row to dict
                    user_dict = {key: user[key] for key in user.keys()}
                    
                    # Check if user already exists
                    existing_user = User.query.filter_by(email=user_dict['email']).first()
                    if existing_user:
                        print(f"  User with email {user_dict['email']} already exists. Skipping.")
                        continue
                    
                    # Create User instance
                    new_user = User(
                        id=user_dict.get('id'),
                        email=user_dict.get('email'),
                        password_hash=user_dict.get('password_hash'),
                        first_name=user_dict.get('first_name'),
                        last_name=user_dict.get('last_name'),
                        phone=user_dict.get('phone'),
                        is_active=user_dict.get('is_active', True),
                        is_verified=user_dict.get('is_verified', False)
                    )
                    
                    # Set timestamps if they exist
                    if 'created_at' in user_dict and user_dict['created_at']:
                        new_user.created_at = datetime.fromisoformat(user_dict['created_at'])
                    
                    if 'updated_at' in user_dict and user_dict['updated_at']:
                        new_user.updated_at = datetime.fromisoformat(user_dict['updated_at'])
                        
                    if 'last_login' in user_dict and user_dict['last_login']:
                        new_user.last_login = datetime.fromisoformat(user_dict['last_login'])
                    
                    # Add to database
                    db.session.add(new_user)
                    migrated_count += 1
                
                # Commit all users
                db.session.commit()
                print(f"  Migrated {migrated_count} users successfully.")
            else:
                print("No users found to migrate.")
                
            # Commit all changes
            db.session.commit()
            print("\nMigration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR during migration: {str(e)}")
        finally:
            # Clean up connections
            sqlite_conn.close()
            mssql_conn.close()
            print("\nDatabase connections closed.")

if __name__ == "__main__":
    migrate_from_sqlite()
