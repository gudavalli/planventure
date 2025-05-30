import json
import pytest
from models.question import Question, ReadingComprehensionSet

def test_create_question(client, setup_database):
    """Test creating a new question"""
    data = {
        'question_type': 'multiple_choice',
        'specialization': 'aptitude',
        'content': 'What is 2+2?',
        'options': ['3', '4', '5', '6'],
        'correct_answer': '4'
    }
    response = client.post('/api/questions',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_create_question_invalid_data(client, setup_database):
    """Test creating a question with missing required fields"""
    data = {
        # Missing content field completely
        'specialization': 'aptitude',
        'options': ['1', '2', '3', '4']
    }
    response = client.post('/api/questions',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 400

def test_get_questions(client, setup_database):
    """Test getting all questions"""
    # Create a test question first
    create_result = json.loads(client.post('/api/questions',
        data=json.dumps({
            'specialization': 'aptitude',
            'content': 'Test question',
            'options': ['1', '2'],
            'correct_answer': '2'
        }),
        content_type='application/json').data)
    
    response = client.get('/api/questions')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['content'] == 'Test question'

def test_get_questions_by_specialization(client, setup_database):
    """Test filtering questions by specialization"""
    # Create questions of different types
    aptitude_data = {
        'specialization': 'aptitude',
        'content': 'Aptitude question',
        'options': ['1', '2'],
        'correct_answer': '2'
    }
    typing_data = {
        'specialization': 'typing',
        'content': 'Typing test',
        'options': None,
        'correct_answer': None
    }
    
    client.post('/api/questions',
               data=json.dumps(aptitude_data),
               content_type='application/json')
    client.post('/api/questions',
               data=json.dumps(typing_data),
               content_type='application/json')
    
    response = client.get('/api/questions?specialization=aptitude')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['specialization'] == 'aptitude'

def test_update_question(client, setup_database):
    """Test updating a question"""
    # Create a test question first
    create_response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'aptitude',
            'content': 'Original content',
            'options': ['1', '2'],
            'correct_answer': '2'
        }),
        content_type='application/json')
    question_id = json.loads(create_response.data)['id']
    
    # Update the question
    update_data = {
        'content': 'Updated content'
    }
    response = client.put(f'/api/questions/{question_id}',
                        data=json.dumps(update_data),
                        content_type='application/json')
    
    assert response.status_code == 200
    
    # Verify the update
    get_response = client.get('/api/questions')
    questions = json.loads(get_response.data)
    assert questions[0]['content'] == 'Updated content'

def test_delete_question(client, setup_database):
    """Test deleting a question"""
    # Create a test question first
    create_response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'aptitude',
            'content': 'To be deleted',
            'options': ['1', '2'],
            'correct_answer': '2'
        }),
        content_type='application/json')
    question_id = json.loads(create_response.data)['id']
    
    # Delete the question
    response = client.delete(f'/api/questions/{question_id}')
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get('/api/questions')
    questions = json.loads(get_response.data)
    assert len(questions) == 0

def test_create_aptitude_question(client, setup_database):
    """Test creating an aptitude question with options"""
    data = {
        'specialization': 'aptitude',
        'content': 'What is 2 + 2?',
        'options': ['1', '2', '3', '4', '5'],
        'correct_answer': '4'
    }
    response = client.post('/api/questions',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_create_reading_comprehension_set(client, setup_database):
    """Test creating a reading comprehension set with paragraph and questions"""
    # First create the reading set
    set_data = {
        'paragraph': 'This is a sample paragraph about Python programming. Python is a versatile language.',
        'specialization': 'reading_comprehension'
    }
    set_response = client.post('/api/reading-sets',
                             data=json.dumps(set_data),
                             content_type='application/json')
    assert set_response.status_code == 201
    reading_set_id = json.loads(set_response.data)['id']
    
    # Create questions linked to the reading set
    questions = [
        {
            'specialization': 'reading_comprehension',
            'content': 'What is Python described as?',
            'options': ['Difficult', 'Versatile', 'Slow', 'Complex'],
            'correct_answer': 'Versatile',
            'reading_set_id': reading_set_id
        },
        {
            'specialization': 'reading_comprehension',
            'content': 'What is the paragraph about?',
            'options': ['Java', 'Python', 'JavaScript', 'C++'],
            'correct_answer': 'Python',
            'reading_set_id': reading_set_id
        }
    ]
    
    for question in questions:
        response = client.post('/api/questions',
                             data=json.dumps(question),
                             content_type='application/json')
        assert response.status_code == 201

    # Get the reading set with questions
    response = client.get(f'/api/reading-sets/{reading_set_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['questions']) == 2

def test_create_typing_question(client, setup_database):
    """Test creating a typing question"""
    data = {
        'specialization': 'typing',
        'content': 'The quick brown fox jumps over the lazy dog.\nPython is a great programming language.\nThis is a typing test.',
        'correct_answer': None  # Typing questions don't have predefined correct answers
    }
    response = client.post('/api/questions',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    question_id = json.loads(response.data)['id']
    
    # Verify the content is properly split into lines
    response = client.get(f'/api/questions/{question_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['content'].split('\n')) == 3  # Should have 3 lines

def test_validate_typing_response(client, setup_database):
    """Test validating a typing response for accuracy and speed"""
    # Create typing question
    question_data = {
        'specialization': 'typing',
        'content': 'The quick brown fox jumps over the lazy dog.',
    }
    question_response = client.post('/api/questions',
                                 data=json.dumps(question_data),
                                 content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Submit a typing response
    response_data = {
        'question_id': question_id,
        'user_response': 'The quick brown fox jumps over the lazy dog.',
        'time_taken_ms': 5000  # 5 seconds
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'accuracy_percentage' in result
    assert 'words_per_minute' in result
    assert result['accuracy_percentage'] == 100.0

def test_invalid_typing_response(client, setup_database):
    """Test typing response with errors"""
    # Create typing question
    question_data = {
        'specialization': 'typing',
        'content': 'The quick brown fox jumps over the lazy dog.',
    }
    question_response = client.post('/api/questions',
                                 data=json.dumps(question_data),
                                 content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Submit a typing response with errors
    response_data = {
        'question_id': question_id,
        'user_response': 'The quik brown fx jumps over the lasy dog.',  # Has typos
        'time_taken_ms': 5000
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['accuracy_percentage'] < 100.0
    assert 'error_positions' in result
