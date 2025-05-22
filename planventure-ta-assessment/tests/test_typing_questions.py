import json
import pytest

def test_typing_empty_response(client, setup_database):
    """Test typing validation with empty response"""
    # Create typing question
    question_data = {
        'specialization': 'typing',
        'content': 'Test typing content.',
    }
    question_response = client.post('/api/questions',
                                data=json.dumps(question_data),
                                content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Submit an empty typing response
    response_data = {
        'question_id': question_id,
        'user_response': '',  # Empty response
        'time_taken_ms': 1000
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['accuracy_percentage'] == 0.0
    assert 'words_per_minute' in result
    assert result['words_per_minute'] == 0.0

def test_typing_special_characters(client, setup_database):
    """Test typing validation with special characters"""
    # Create typing question with special characters
    question_data = {
        'specialization': 'typing',
        'content': 'Special chars: !@#$%^&*()_+-={}[]|\\:;"\'<>,.?/',
    }
    question_response = client.post('/api/questions',
                                data=json.dumps(question_data),
                                content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Submit a matching response
    response_data = {
        'question_id': question_id,
        'user_response': 'Special chars: !@#$%^&*()_+-={}[]|\\:;"\'<>,.?/',
        'time_taken_ms': 10000
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['accuracy_percentage'] == 100.0
    assert 'error_positions' in result
    assert len(result['error_positions']) == 0

def test_typing_wpm_calculation(client, setup_database):
    """Test words per minute calculation at different speeds"""
    # Create a typing question with known word count (5 words)
    question_data = {
        'specialization': 'typing',
        'content': 'This is five words total.',
    }
    question_response = client.post('/api/questions',
                                data=json.dumps(question_data),
                                content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Test with 1 minute (60000ms)
    response_data = {
        'question_id': question_id,
        'user_response': 'This is five words total.',
        'time_taken_ms': 60000  # 1 minute
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    result = json.loads(response.data)
    assert result['words_per_minute'] == 5.0  # 5 words in 1 minute = 5 WPM
    
    # Test with 30 seconds (30000ms)
    response_data['time_taken_ms'] = 30000  # 30 seconds
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    result = json.loads(response.data)
    assert result['words_per_minute'] == 10.0  # 5 words in 30 seconds = 10 WPM
    
    # Test with 15 seconds (15000ms) 
    response_data['time_taken_ms'] = 15000  # 15 seconds
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    result = json.loads(response.data)
    assert result['words_per_minute'] == 20.0  # 5 words in 15 seconds = 20 WPM

def test_typing_long_text(client, setup_database):
    """Test typing validation with very long text"""
    # Create a long typing question (paragraph repeated multiple times)
    paragraph = "This is a test paragraph with multiple sentences. It contains various words of different lengths to simulate a realistic typing test. The purpose is to test how the system handles longer text inputs."
    long_content = "\n".join([paragraph] * 5)  # Repeat 5 times
    
    question_data = {
        'specialization': 'typing',
        'content': long_content,
    }
    question_response = client.post('/api/questions',
                                data=json.dumps(question_data),
                                content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Create a response with one error per paragraph
    paragraphs = long_content.split("\n")
    modified_paragraphs = []
    
    for p in paragraphs:
        # Introduce a single typo in each paragraph
        modified_p = p.replace("test", "text").replace("Test", "Text", 1)
        modified_paragraphs.append(modified_p)
        
    user_response = "\n".join(modified_paragraphs)
    
    response_data = {
        'question_id': question_id,
        'user_response': user_response,
        'time_taken_ms': 60000  # 1 minute
    }
    response = client.post('/api/questions/typing/validate',
                         data=json.dumps(response_data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    
    # There should be errors (at least one in each paragraph)
    assert result['accuracy_percentage'] < 100.0
    assert len(result['error_positions']) > 0
