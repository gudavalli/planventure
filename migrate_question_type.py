#!/usr/bin/env python3
"""
Quick script to run the SQLite migration to add the question_type field.
This script updates the questions table to include the new field.
"""
import sqlite3
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_path():
    """Find the SQLite database file"""
    # Check common locations with correct path
    possible_paths = [
        './planventure-ta-assessment/instance/assessment.db',
        './instance/assessment.db',
        './assessment.db',
        './planventure-ta-assessment/instance/assessment.db',
        # Add the exact path we found
        'planventure-ta-assessment/instance/assessment.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found database at: {path}")
            return path
    
    return None

def run_migration():
    """Add question_type column and populate it based on specialization values"""
    db_path = get_db_path()
    if not db_path:
        logger.error("Database file not found")
        return False
    
    logger.info(f"Using database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(questions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Add the column if it doesn't exist
        if 'question_type' not in column_names:
            logger.info("Adding question_type column to questions table...")
            cursor.execute("ALTER TABLE questions ADD COLUMN question_type VARCHAR(50)")
            logger.info("Column added successfully")
        else:
            logger.info("question_type column already exists")
        
        # Update the column values based on specialization
        logger.info("Updating question_type values based on specialization...")
        cursor.execute("""
            UPDATE questions
            SET question_type = CASE
                WHEN specialization = 'reading_comprehension' THEN 'reading_comprehension'
                WHEN specialization = 'typing' THEN 'typing'
                ELSE 'multiple_choice'
            END
            WHERE question_type IS NULL
        """)
        
        conn.commit()
        updated_rows = cursor.rowcount
        logger.info(f"Updated {updated_rows} rows")
        
        # Verify the update
        cursor.execute("SELECT id, specialization, question_type FROM questions LIMIT 10")
        sample_rows = cursor.fetchall()
        
        if sample_rows:
            logger.info("Sample data after migration:")
            for row in sample_rows:
                logger.info(f"ID: {row[0]}, Specialization: {row[1]}, Question Type: {row[2]}")
        
        conn.close()
        return True
    
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting SQLite migration to add question_type field")
    success = run_migration()
    
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1)
