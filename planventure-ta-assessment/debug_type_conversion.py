#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db
from models.question import Question
import json

def test_type_conversion():
    print("Starting type conversion test...")
    app = create_app()
    print("App created successfully")
    
    with app.app_context():
        print("App context established")
        with app.test_client() as client:
            print("Test client created")
            # Test 1: Create a question with integer correct_answer
            print("=== TEST 1: Creating question with integer correct_answer ===")
            data = {
                'specialization': 'aptitude',
                'content': 'Test question',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 1,  # This is an integer
                'explanation': 'Test explanation'
            }
            
            print(f"Sending data: {data}")
            print(f"correct_answer type: {type(data['correct_answer'])}")
            
            response = client.post('/api/questions',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 201:
                result = json.loads(response.data)
                question_id = result['id']
                print(f"Question created with ID: {question_id}")
                
                # Check what's stored in the database
                question = Question.query.get(question_id)
                print(f"Database correct_answer: {repr(question.correct_answer)}")
                print(f"Database correct_answer type: {type(question.correct_answer)}")
                
                # Test 2: Update with string that looks like a number
                print("\n=== TEST 2: Updating with string '2' ===")
                update_data = {
                    'correct_answer': '2'  # This is a string
                }
                
                print(f"Sending update data: {update_data}")
                print(f"correct_answer type: {type(update_data['correct_answer'])}")
                
                update_response = client.put(f'/api/questions/{question_id}',
                                           data=json.dumps(update_data),
                                           content_type='application/json')
                
                print(f"Update response status: {update_response.status_code}")
                
                # Check what's stored after update
                question = Question.query.get(question_id)
                print(f"After update - Database correct_answer: {repr(question.correct_answer)}")
                print(f"After update - Database correct_answer type: {type(question.correct_answer)}")
                
            else:
                print(f"Failed to create question: {response.data}")

if __name__ == '__main__':
    test_type_conversion()
