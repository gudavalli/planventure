#!/usr/bin/env python3
"""
Migration script to add question_type field to the questions table
and populate it based on existing specialization values.

This script differentiates between question format (question_type) and subject area (specialization).
"""
from app import create_app

app = create_app()
from models.database import db
from models.question import Question
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_question_types():
    """Add question_type field and populate it based on existing data"""
    try:
        with app.app_context():
            # First check if column exists
            check_sql = text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name='questions' AND column_name='question_type'")
            result = db.session.execute(check_sql).scalar()
            
            if result == 0:
                logger.info("Adding question_type column to questions table...")
                # Add the new column if it doesn't exist
                add_column_sql = text("ALTER TABLE questions ADD COLUMN question_type VARCHAR(50)")
                db.session.execute(add_column_sql)
                db.session.commit()
                logger.info("Column added successfully")
            else:
                logger.info("question_type column already exists")
            
            # Map old specialization values to new question_type values
            type_mapping = {
                'aptitude': 'multiple_choice',
                'reading_comprehension': 'reading_comprehension',
                'typing': 'typing'
            }
            
            # Fetch all questions and update the question_type field
            questions = Question.query.all()
            total = len(questions)
            logger.info(f"Found {total} questions to update")
            
            updated = 0
            for question in questions:
                old_type = question.specialization
                
                # Set the question_type based on the old specialization value
                if old_type in type_mapping:
                    question.question_type = type_mapping[old_type]
                else:
                    # Default to multiple_choice if unknown
                    question.question_type = 'multiple_choice'
                
                # Keep the original specialization value as the subject area
                # For now, we'll maintain backward compatibility
                
                updated += 1
                if updated % 100 == 0:
                    logger.info(f"Updated {updated}/{total} questions")
            
            db.session.commit()
            logger.info(f"Migration completed successfully. Updated {updated} questions.")
            
            return True
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    success = migrate_question_types()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed. Check the logs for details.")
