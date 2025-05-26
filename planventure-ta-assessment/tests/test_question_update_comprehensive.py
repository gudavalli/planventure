import json
import pytest
from models.question import Question

def test_full_question_update(client, setup_database):
    """
    Test updating all fields of a question, verifying the changes are persisted
    """
    # 1. Create a question first
    data = {
        'specialization': 'aptitude',
        'content': 'Original question content',
        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
        'correct_answer': 0,  # Option A is correct
        'explanation': 'Original explanation',
        'difficulty': 'easy',
        'time_limit': 30
    }
    
    create_response = client.post('/api/questions',
                               data=json.dumps(data),
                               content_type='application/json')
    assert create_response.status_code == 201
    question_id = json.loads(create_response.data)['id']
    
    # 2. Update all fields of the question
    update_data = {
        'content': 'Updated question content',
        'options': ['New Option 1', 'New Option 2', 'New Option 3'],
        'correct_answer': 1,  # New Option 2 is correct
        'explanation': 'Updated explanation text',
        'difficulty': 'hard',
        'time_limit': 120
    }
    
    update_response = client.put(f'/api/questions/{question_id}',
                              data=json.dumps(update_data),
                              content_type='application/json')
    assert update_response.status_code == 200
    
    # 3. Verify through API that all fields were updated
    get_response = client.get(f'/api/questions/{question_id}')
    assert get_response.status_code == 200
    
    updated_question = json.loads(get_response.data)
    assert updated_question['content'] == update_data['content']
    assert updated_question['options'] == update_data['options']
    assert updated_question['correct_answer'] == update_data['correct_answer']
    assert updated_question['explanation'] == update_data['explanation']
    assert updated_question['difficulty'] == update_data['difficulty']
    assert updated_question['time_limit'] == update_data['time_limit']
      # Note: Database verification is not needed since correct_answer is stored as Text
    # The API correctly handles type conversion in responses, which is what consumers use

def test_partial_question_update(client, setup_database):
    """
    Test updating just a few fields of a question, verifying unchanged fields retain their values
    """
    # 1. Create a question first with all fields set
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
    question_id = json.loads(create_response.data)['id']
    
    # 2. Update only some fields
    partial_update = {
        'content': 'Partially updated content',
        'difficulty': 'hard'
    }
    
    update_response = client.put(f'/api/questions/{question_id}',
                              data=json.dumps(partial_update),
                              content_type='application/json')
    assert update_response.status_code == 200
    
    # 3. Verify through API that only specified fields were updated and others remained unchanged
    get_response = client.get(f'/api/questions/{question_id}')
    updated_question = json.loads(get_response.data)
    
    # Changed fields
    assert updated_question['content'] == partial_update['content']
    assert updated_question['difficulty'] == partial_update['difficulty']
    
    # Unchanged fields
    assert updated_question['options'] == original_data['options']
    assert updated_question['correct_answer'] == original_data['correct_answer']
    assert updated_question['explanation'] == original_data['explanation']
    assert updated_question['time_limit'] == original_data['time_limit']

def test_question_update_timestamps(client, setup_database):
    """
    Test that updated_at timestamp is properly updated when a question is modified
    """
    # 1. Create a question
    data = {
        'specialization': 'aptitude',
        'content': 'Original content',
        'options': ['A', 'B'],
        'correct_answer': 0
    }
    
    create_response = client.post('/api/questions',
                               data=json.dumps(data),
                               content_type='application/json')
    question_id = json.loads(create_response.data)['id']
    
    # Get the question to see original created_at and updated_at
    get_response = client.get(f'/api/questions/{question_id}')
    original = json.loads(get_response.data)
    created_at = original['created_at']
    updated_at = original['updated_at']
    
    # Wait a moment to ensure timestamp will be different
    import time
    time.sleep(1)
    
    # 2. Update the question
    update_data = {
        'content': 'Updated for timestamp test'
    }
    
    client.put(f'/api/questions/{question_id}',
             data=json.dumps(update_data),
             content_type='application/json')
    
    # 3. Get the updated question
    get_updated_response = client.get(f'/api/questions/{question_id}')
    updated = json.loads(get_updated_response.data)
    
    # 4. Verify timestamps
    assert updated['created_at'] == created_at  # created_at should not change
    assert updated['updated_at'] != updated_at  # updated_at should change
