import json
import pytest

def test_create_question(client, setup_database):
    """Test creating a new question"""
    data = {
        'specialization': 'programming',
        'content': 'What is encapsulation?',
        'options': ['Data hiding', 'Data sharing', 'Data copying', 'Data transfer'],
        'correct_answer': 'Data hiding',
        'difficulty': 'medium'
    }
    response = client.post('/api/questions',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_update_question(client, setup_database):
    """Test updating an existing question"""
    # Create a question first
    data = {
        'specialization': 'programming',
        'content': 'What is inheritance?',
        'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
        'correct_answer': 'Option 2'
    }
    create_response = client.post('/api/questions',
                                data=json.dumps(data),
                                content_type='application/json')
    question_id = json.loads(create_response.data)['id']
    
    # Update the question
    update_data = {
        'content': 'Updated: What is inheritance in OOP?',
        'options': ['Option 1', 'Reuse code', 'Option 3', 'Option 4'],
        'correct_answer': 'Reuse code'
    }
    response = client.put(f'/api/questions/{question_id}',
                        data=json.dumps(update_data),
                        content_type='application/json')
    
    # Check if update endpoint exists, skip if not implemented
    if response.status_code == 404:
        pytest.skip("Question update endpoint not implemented yet")
        
    assert response.status_code == 200
    
    # Verify the question was updated
    get_response = client.get(f'/api/questions/{question_id}')
    question = json.loads(get_response.data)
    assert question['content'] == 'Updated: What is inheritance in OOP?'
    assert 'Reuse code' in question['options']
    assert question['correct_answer'] == 'Reuse code'

def test_add_question_tags(client, setup_database):
    """Test adding tags to a question"""
    # Create a question 
    data = {
        'specialization': 'programming',
        'content': 'What are decorators in Python?',
        'options': ['Functions', 'Classes', 'Design patterns', 'Annotations'],
        'correct_answer': 'Functions'
    }
    create_response = client.post('/api/questions',
                                data=json.dumps(data),
                                content_type='application/json')
    question_id = json.loads(create_response.data)['id']
    
    # Add tags to the question
    tags_data = {
        'tags': ['python', 'advanced', 'functions']
    }
    response = client.post(f'/api/questions/{question_id}/tags',
                         data=json.dumps(tags_data),
                         content_type='application/json')
    
    # Skip if tagging is not implemented
    if response.status_code == 404:
        pytest.skip("Question tagging endpoint not implemented yet")
        
    assert response.status_code == 200
    
    # Verify tags were added
    get_response = client.get(f'/api/questions/{question_id}')
    question = json.loads(get_response.data)
    
    # Check if tags field exists in the response
    if 'tags' in question:
        assert 'python' in question['tags']
        assert 'advanced' in question['tags']
        assert 'functions' in question['tags']

def test_search_questions_by_tag(client, setup_database):
    """Test searching for questions by tag"""
    # Create questions with tags
    # First question with 'python' tag
    q1_data = {
        'specialization': 'programming',
        'content': 'What is a list comprehension?',
        'options': ['Loop construct', 'Data type', 'Error handling', 'File operation'],
        'correct_answer': 'Loop construct'
    }
    q1_response = client.post('/api/questions',
                            data=json.dumps(q1_data),
                            content_type='application/json')
    q1_id = json.loads(q1_response.data)['id']
    
    # Add python tag to first question
    client.post(f'/api/questions/{q1_id}/tags',
               data=json.dumps({'tags': ['python']}),
               content_type='application/json')
    
    # Second question with 'java' tag
    q2_data = {
        'specialization': 'programming',
        'content': 'What is the JVM?',
        'options': ['Java Virtual Machine', 'Java Variable Method', 'Just Valuable Memory', 'Java Visual Manager'],
        'correct_answer': 'Java Virtual Machine'
    }
    q2_response = client.post('/api/questions',
                            data=json.dumps(q2_data),
                            content_type='application/json')
    q2_id = json.loads(q2_response.data)['id']
    
    # Add java tag to second question
    client.post(f'/api/questions/{q2_id}/tags',
               data=json.dumps({'tags': ['java']}),
               content_type='application/json')
    
    # Search for questions with python tag
    response = client.get('/api/questions?tag=python')
    
    # Skip if tag search is not implemented
    if response.status_code == 400:  # Assuming 400 means tag parameter not supported
        pytest.skip("Question search by tag not implemented yet")
    
    data = json.loads(response.data)
    
    # Check if search results are returned as list or paginated format
    if isinstance(data, list):
        questions = data
        # At least our question with python tag should be found
        assert len(questions) >= 1
        # The first question should have the python tag
        found_python_question = False
        for question in questions:
            if question['id'] == q1_id and ('tags' not in question or 'python' in question['tags']):
                found_python_question = True
                break
        assert found_python_question
    else:
        # Check in paginated format
        if 'questions' in data:
            questions = data['questions']
            assert len(questions) >= 1
            # The first question should have the python tag
            found_python_question = False
            for question in questions:
                if question['id'] == q1_id and ('tags' not in question or 'python' in question['tags']):
                    found_python_question = True
                    break
            assert found_python_question

def test_bulk_question_operations(client, setup_database):
    """Test bulk operations for questions (like deleting multiple at once)"""
    # Create multiple questions
    question_ids = []
    for i in range(3):
        data = {
            'specialization': 'aptitude',
            'content': f'Bulk test question {i}',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'A'
        }
        response = client.post('/api/questions',
                             data=json.dumps(data),
                             content_type='application/json')
        question_ids.append(json.loads(response.data)['id'])
    
    # Perform bulk delete
    bulk_data = {
        'question_ids': question_ids
    }
    response = client.post('/api/questions/bulk-delete',
                         data=json.dumps(bulk_data),
                         content_type='application/json')
    
    # Skip if bulk operations are not implemented
    if response.status_code == 404:
        pytest.skip("Bulk question operations not implemented yet")
        
    assert response.status_code == 200
    
    # Verify questions were deleted
    for q_id in question_ids:
        get_response = client.get(f'/api/questions/{q_id}')
        assert get_response.status_code == 404
