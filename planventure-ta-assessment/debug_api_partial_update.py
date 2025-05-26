#!/usr/bin/env python3
"""
Debug script to test the actual API endpoints for partial updates
"""
import sys
import os
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_api_partial_update():
    try:
        print("Testing API partial update...")
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # 1. Create a question with all fields
            print("=== CREATING QUESTION ===")
            original_data = {
                'specialization': 'aptitude',
                'content': 'Original question content',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0,
                'explanation': 'Original explanation',
                'difficulty': 'medium',
                'time_limit': 60
            }
            
            create_response = client.post('/api/questions',
                                       data=json.dumps(original_data),
                                       content_type='application/json')
            
            print(f"Create response status: {create_response.status_code}")
            print(f"Create response data: {create_response.data.decode()}")
            
            if create_response.status_code != 201:
                print("Failed to create question")
                return
                
            question_id = json.loads(create_response.data)['id']
            print(f"Created question ID: {question_id}")
            
            # 2. Get the question to verify it was created correctly
            print("\n=== GETTING ORIGINAL QUESTION ===")
            get_response = client.get(f'/api/questions/{question_id}')
            print(f"Get response status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                original_question = json.loads(get_response.data)
                print(f"Original content: {original_question.get('content')}")
                print(f"Original explanation: {original_question.get('explanation')}")
                print(f"Original difficulty: {original_question.get('difficulty')}")
                print(f"Original correct_answer: {original_question.get('correct_answer')}")
            
            # 3. Perform partial update
            print("\n=== PERFORMING PARTIAL UPDATE ===")
            partial_update = {
                'content': 'Partially updated content',
                'difficulty': 'hard'
            }
            
            update_response = client.put(f'/api/questions/{question_id}',
                                      data=json.dumps(partial_update),
                                      content_type='application/json')
            
            print(f"Update response status: {update_response.status_code}")
            print(f"Update response data: {update_response.data.decode()}")
            
            # 4. Get the question again to see the result
            print("\n=== GETTING UPDATED QUESTION ===")
            get_updated_response = client.get(f'/api/questions/{question_id}')
            print(f"Get updated response status: {get_updated_response.status_code}")
            
            if get_updated_response.status_code == 200:
                updated_question = json.loads(get_updated_response.data)
                print(f"Updated content: {updated_question.get('content')}")
                print(f"Updated explanation: {updated_question.get('explanation')}")
                print(f"Updated difficulty: {updated_question.get('difficulty')}")
                print(f"Updated correct_answer: {updated_question.get('correct_answer')}")
                
                # Check if unchanged fields preserved
                print("\n=== VERIFICATION ===")
                print(f"Content changed correctly: {updated_question.get('content') == partial_update['content']}")
                print(f"Difficulty changed correctly: {updated_question.get('difficulty') == partial_update['difficulty']}")
                print(f"Explanation preserved: {updated_question.get('explanation') == original_data['explanation']}")
                print(f"Correct answer preserved: {updated_question.get('correct_answer') == original_data['correct_answer']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_partial_update()
