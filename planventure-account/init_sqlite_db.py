"""SQLite database initialization script for PlanVenture Account Service."""
import os
from dotenv import load_dotenv
from app import create_app, db
from models.roles import UserRole
from models.user import User

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the SQLite database schema."""
    print("Initializing SQLite database...")
    
    # Set SQLite database URL
    os.environ['DATABASE_URL'] = 'sqlite:///instance/planventure.db'
    
    # Create tables using SQLAlchemy
    app = create_app()
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Tables created successfully.")
            
            # Create default admin user if it doesn't exist
            admin = User.query.filter_by(email='admin@planventure.com').first()
            if not admin:
                admin = User(
                    email='admin@planventure.com',
                    password='admin123',  # Change this in production
                    role=UserRole.ADMIN.value
                )
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created.")
            
            return True
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            return False

if __name__ == '__main__':
    if init_database():
        print("Database initialization completed successfully.")
    else:
        print("Database initialization encountered errors. Check the output above.")
        exit(1)
