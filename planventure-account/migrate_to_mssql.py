"""Script to migrate data from SQLite to SQL Server."""
import os
import sqlite3
import json
import pyodbc
from datetime import datetime
from dotenv import load_dotenv
from app import create_app, db
from models.user import User
from models.trip import Trip

# Load environment variables
load_dotenv()

def migrate_from_sqlite():
    """Migrate data from SQLite to SQL Server."""
    # Check if SQLite database exists
    if not os.path.exists('instance/planventure.db'):
        print("SQLite database not found. Nothing to migrate.")
        return
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('instance/planventure.db')
    sqlite_conn.row_factory = sqlite3.Row
      # Connect to SQL Server
    server = os.getenv('DB_SERVER', 'localhost,1433')
    username = os.getenv('DB_USERNAME', 'sa')
    password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
    database = os.getenv('DB_NAME', 'planventure')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    print(f"Connecting to SQL Server at {server}...")
    try:
        mssql_conn = pyodbc.connect(conn_str, autocommit=True)
        print("Connected successfully to SQL Server.")
    except Exception as e:
        print(f"Error connecting to SQL Server: {str(e)}")
        return
    
    # Create Flask app context to use models
    app = create_app()
    
    with app.app_context():
        # Ensure tables exist in SQL Server
        db.create_all()        # Migrate users
        print("Migrating users...")
        try:
            # Get the table name - in SQLite it might be 'user', in the new schema it's 'users'
            sqlite_user_table = 'user'  # Check if 'users' exists first
            try:
                sqlite_conn.execute("SELECT 1 FROM users LIMIT 1")
                sqlite_user_table = 'users'
            except:
                pass
                
            users = sqlite_conn.execute(f'SELECT * FROM {sqlite_user_table}').fetchall()
            if users:
                cursor = mssql_conn.cursor()
                migrated_count = 0
                
                for user in users:
                    try:
                        # Convert SQLite row to dict
                        user_dict = {key: user[key] for key in user.keys()}
                        
                        # Create a User model instance
                        new_user = User(
                            email=user_dict.get('email'),
                            password='placeholder'  # We'll update this after
                        )
                        
                        # Set attributes directly to preserve existing IDs and timestamps
                        new_user.id = user_dict.get('id')
                        new_user.password_hash = user_dict.get('password_hash')
                        new_user.is_active = user_dict.get('is_active', True)
                        new_user.is_verified = user_dict.get('is_verified', False)
                        new_user.first_name = user_dict.get('first_name')
                        new_user.last_name = user_dict.get('last_name')
                        new_user.phone = user_dict.get('phone')
                        
                        # Handle timestamps
                        if 'created_at' in user_dict and user_dict['created_at']:
                            new_user.created_at = datetime.fromisoformat(user_dict['created_at'])
                        if 'updated_at' in user_dict and user_dict['updated_at']:
                            new_user.updated_at = datetime.fromisoformat(user_dict['updated_at'])
                        if 'last_login' in user_dict and user_dict['last_login']:
                            new_user.last_login = datetime.fromisoformat(user_dict['last_login'])
                            
                        # Handle verification tokens
                        new_user.verification_token = user_dict.get('verification_token')
                        if 'verification_token_expires' in user_dict and user_dict['verification_token_expires']:
                            new_user.verification_token_expires = datetime.fromisoformat(user_dict['verification_token_expires'])
                        
                        new_user.reset_token = user_dict.get('reset_token')
                        if 'reset_token_expires' in user_dict and user_dict['reset_token_expires']:
                            new_user.reset_token_expires = datetime.fromisoformat(user_dict['reset_token_expires'])
                        
                        # Check if user already exists
                        existing_user = User.query.get(new_user.id)
                        if existing_user:
                            print(f"User with id {new_user.id} already exists, skipping...")
                            continue
                        
                        # Add to database
                        db.session.add(new_user)
                        db.session.commit()
                        migrated_count += 1
                    except Exception as e:
                        print(f"Error migrating user {user_dict.get('email')}: {str(e)}")
                        db.session.rollback()
                
                print(f"Successfully migrated {migrated_count} users.")
            else:
                print("No users found to migrate.")
                
            # Migrate trips
            print("\nMigrating trips...")
            try:
                # Check if trips table exists in SQLite
                try:
                    sqlite_conn.execute("SELECT 1 FROM trips LIMIT 1")
                    has_trips = True
                except:
                    has_trips = False
                
                if has_trips:
                    trips = sqlite_conn.execute('SELECT * FROM trips').fetchall()
                    if trips:
                        migrated_count = 0
                        
                        for trip in trips:
                            try:
                                # Convert SQLite row to dict
                                trip_dict = {key: trip[key] for key in trip.keys()}
                                
                                # Parse dates
                                start_date = None
                                if 'start_date' in trip_dict and trip_dict['start_date']:
                                    start_date = datetime.fromisoformat(trip_dict['start_date']).date()
                                
                                end_date = None
                                if 'end_date' in trip_dict and trip_dict['end_date']:
                                    end_date = datetime.fromisoformat(trip_dict['end_date']).date()
                                
                                # Parse itinerary (might be stored as JSON string)
                                itinerary = {}
                                if 'itinerary' in trip_dict and trip_dict['itinerary']:
                                    if isinstance(trip_dict['itinerary'], str):
                                        try:
                                            itinerary = json.loads(trip_dict['itinerary'])
                                        except:
                                            itinerary = {"data": trip_dict['itinerary']}
                                    else:
                                        itinerary = trip_dict['itinerary']
                                
                                # Create Trip instance
                                new_trip = Trip(
                                    user_id=trip_dict.get('user_id'),
                                    title=trip_dict.get('title', 'Untitled Trip'),
                                    destination=trip_dict.get('destination', 'Unknown'),
                                    start_date=start_date,
                                    end_date=end_date,
                                    description=trip_dict.get('description'),
                                    latitude=trip_dict.get('latitude'),
                                    longitude=trip_dict.get('longitude'),
                                    itinerary=itinerary,
                                    is_public=trip_dict.get('is_public', False),
                                    status=trip_dict.get('status', 'planning')
                                )
                                
                                # Set ID to preserve references
                                new_trip.id = trip_dict.get('id')
                                
                                # Handle timestamps
                                if 'created_at' in trip_dict and trip_dict['created_at']:
                                    new_trip.created_at = datetime.fromisoformat(trip_dict['created_at'])
                                if 'updated_at' in trip_dict and trip_dict['updated_at']:
                                    new_trip.updated_at = datetime.fromisoformat(trip_dict['updated_at'])
                                
                                # Check if trip already exists
                                existing_trip = Trip.query.get(new_trip.id)
                                if existing_trip:
                                    print(f"Trip with id {new_trip.id} already exists, skipping...")
                                    continue
                                
                                # Add to database
                                db.session.add(new_trip)
                                db.session.commit()
                                migrated_count += 1
                            except Exception as e:
                                print(f"Error migrating trip {trip_dict.get('id')}: {str(e)}")
                                db.session.rollback()
                        
                        print(f"Successfully migrated {migrated_count} trips.")
                    else:
                        print("No trips found to migrate.")
                else:
                    print("Trips table does not exist in SQLite, skipping...")
            except Exception as e:
                print(f"Error during trip migration: {str(e)}")
            
            print("\nMigration completed successfully.")
        except Exception as e:
            print(f"Migration failed: {str(e)}")
    
    # Close connections
    sqlite_conn.close()
    mssql_conn.close()

if __name__ == "__main__":
    migrate_from_sqlite()
