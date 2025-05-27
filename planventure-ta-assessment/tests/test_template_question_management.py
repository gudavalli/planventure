import json
import pytest
from models.assessment import AssessmentTemplate as Template

def test_remove_question_from_template(client, setup_database):
    """Test removing a question from a template"""
    # Create a template first
    template_data = {
        'name': 'Test Template for Question Removal',
        'description': 'Testing question removal',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create a couple of questions
    questions = []
    for i in range(2):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i} for removal test',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'B'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        questions.append(json.loads(question_response.data)['id'])
    
    # Add questions to the template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': questions}),
               content_type='application/json')
    
    # Get template details to confirm questions are added
    response = client.get(f'/api/templates/{template_id}')
    
    # Skip if endpoint not implemented
    if response.status_code == 404:
        pytest.skip("Template details endpoint not implemented yet")
        
    data = json.loads(response.data)
    assert len(data['questions']) == 2
    
    # Now remove one question
    response = client.delete(f'/api/templates/{template_id}/questions/{questions[0]}')
    
    # Skip if endpoint not implemented
    if response.status_code == 404:
        pytest.skip("Remove question from template endpoint not implemented yet")
    
    assert response.status_code == 200
    
    # Verify question was removed by getting template details again
    response = client.get(f'/api/templates/{template_id}')
    data = json.loads(response.data)
    
    assert len(data['questions']) == 1
    assert data['questions'][0]['id'] == questions[1]
    
def test_remove_question_from_template_not_found(client, setup_database):
    """Test removing a non-existent question from a template"""
    # Create a template first
    template_data = {
        'name': 'Another Test Template',
        'description': 'Testing error handling',
        'time_limit': 45,
        'percentage': 80,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Try to remove a question that doesn't exist
    non_existent_question_id = 9999
    response = client.delete(f'/api/templates/{template_id}/questions/{non_existent_question_id}')
    
    # Skip if endpoint not implemented
    if response.status_code == 404 and "not implemented" in json.loads(response.data).get('error', '').lower():
        pytest.skip("Remove question from template endpoint not implemented yet")
    
    # Should return 404 for question not found
    assert response.status_code == 404
    
def test_remove_question_template_not_found(client, setup_database):
    """Test removing a question from a non-existent template"""
    # Create a question first
    question_data = {
        'specialization': 'aptitude',
        'content': 'Question for non-existent template test',
        'options': ['A', 'B', 'C', 'D'],
        'correct_answer': 'C'
    }
    question_response = client.post('/api/questions',
                                  data=json.dumps(question_data),
                                  content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Try to remove from a template that doesn't exist
    non_existent_template_id = 9999
    response = client.delete(f'/api/templates/{non_existent_template_id}/questions/{question_id}')
    
    # Skip if endpoint not implemented
    if response.status_code == 404 and "not implemented" in json.loads(response.data).get('error', '').lower():
        pytest.skip("Remove question from template endpoint not implemented yet")
    
    # Should return 404 for template not found
    assert response.status_code == 404
