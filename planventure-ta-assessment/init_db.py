from app import create_app
from models.database import db
import os

def setup_database():
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Create all tables
    app = create_app()
    with app.app_context():
        db.create_all()
    
if __name__ == '__main__':
    setup_database()
    print("Database initialized successfully.")
