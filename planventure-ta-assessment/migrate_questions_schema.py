"""
This script adds the new columns to the questions table:
- explanation (Text)
- difficulty (String)
- time_limit (Integer)

Run this script once to update the database schema.
"""
import os
from flask import Flask
from models.database import db
from sqlalchemy import Column, Text, String, Integer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Use the same pattern as in the main app.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'assessment.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance directory exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

db.init_app(app)

def migrate_schema():
    with app.app_context():
        connection = db.engine.connect()
        
        # Check if columns already exist before adding them
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('questions')]
        
        if 'explanation' not in columns:
            logger.info("Adding explanation column to questions table")
            connection.execute(db.text("ALTER TABLE questions ADD COLUMN explanation TEXT"))
        else:
            logger.info("explanation column already exists")
            
        if 'difficulty' not in columns:
            logger.info("Adding difficulty column to questions table")
            connection.execute(db.text("ALTER TABLE questions ADD COLUMN difficulty VARCHAR(10) DEFAULT 'medium'"))
        else:
            logger.info("difficulty column already exists")
            
        if 'time_limit' not in columns:
            logger.info("Adding time_limit column to questions table")
            connection.execute(db.text("ALTER TABLE questions ADD COLUMN time_limit INTEGER DEFAULT 60"))
        else:
            logger.info("time_limit column already exists")
            
        db.session.commit()
        logger.info("Schema migration complete")

if __name__ == '__main__':
    migrate_schema()
