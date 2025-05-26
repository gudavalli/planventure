#!/usr/bin/env python3
"""
Debug script to test partial question updates
"""
import sys
import os
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db
from models.question import Question

def test_partial_update():
    try:
        print("Starting debug test...")
        # Create test app
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_debug.db'
        
        with app.app_context():
            # Create tables
            db.create_all()
            
            # Create a test question
            question = Question(
                specialization='aptitude',
                content='Original question content',
                options=['Option A', 'Option B', 'Option C', 'Option D'],
                correct_answer='0',  # Store as string like the actual app does
                explanation='Original explanation',
                difficulty='medium',
                time_limit=60
            )
            
            db.session.add(question)
            db.session.commit()
            
            print("=== ORIGINAL QUESTION ===")
            print(f"ID: {question.id}")
            print(f"Content: {question.content}")
            print(f"Explanation: {question.explanation}")
            print(f"Correct Answer: {question.correct_answer}")
            print(f"Difficulty: {question.difficulty}")
            print()
            
            # Simulate partial update (only content and difficulty)
            question_id = question.id
            
            # Re-fetch the question (like the endpoint does)
            question = Question.query.get(question_id)
            
            # Apply partial update
            question.content = 'Partially updated content'
            question.difficulty = 'hard'
            
            db.session.commit()
            
            # Fetch again to see the result
            updated_question = Question.query.get(question_id)
            
            print("=== AFTER PARTIAL UPDATE ===")
            print(f"Content: {updated_question.content}")
            print(f"Explanation: {updated_question.explanation}")
            print(f"Correct Answer: {updated_question.correct_answer}")
            print(f"Difficulty: {updated_question.difficulty}")
            print()
            
            # Check what happens if we query it again
            fresh_question = Question.query.get(question_id)
            
            print("=== FRESH QUERY ===")
            print(f"Content: {fresh_question.content}")
            print(f"Explanation: {fresh_question.explanation}")
            print(f"Correct Answer: {fresh_question.correct_answer}")
            print(f"Difficulty: {fresh_question.difficulty}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_partial_update()
