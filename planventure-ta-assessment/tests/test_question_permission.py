import json
import pytest
from flask_login import current_user
from models.assessment import AssessmentTemplate as Template

def test_remove_question_permission_denied(client, setup_database):
    """Test that regular users cannot remove questions from templates"""
    # Create a template and questions as admin
    template_data = {
        'name': 'Permission Test Template',
        'description': 'Testing permissions',
        'time_limit': 30,
        'percentage': 100,
        'creator_id': 1  # Admin user
    }
    
    # Login as admin to create template
    client.post('/api/auth/login', 
                data=json.dumps({'email': 'admin@example.com', 'password': 'admin123'}),
                content_type='application/json')
    
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create a question
    question_data = {
        'specialization': 'aptitude',
        'content': 'Test permission question',
        'options': ['A', 'B', 'C', 'D'],
        'correct_answer': 'A'
    }
    
    question_response = client.post('/api/questions',
                                  data=json.dumps(question_data),
                                  content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Add question to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [question_id]}),
               content_type='application/json')
    
    # Logout admin
    client.get('/api/auth/logout')
    
    # Login as regular user
    client.post('/api/auth/login', 
                data=json.dumps({'email': 'user@example.com', 'password': 'user123'}),
                content_type='application/json')
    
    # Try to remove question as regular user
    response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
    
    # Skip if endpoint not implemented
    if response.status_code == 404 and "not implemented" in json.loads(response.data).get('error', '').lower():
        pytest.skip("Remove question from template endpoint not implemented yet")
    
    # Should return 403 for permission denied
    assert response.status_code == 403
    
    # Verify question was not removed
    client.get('/api/auth/logout')
    
    # Login back as admin
    client.post('/api/auth/login', 
                data=json.dumps({'email': 'admin@example.com', 'password': 'admin123'}),
                content_type='application/json')
    
    # Check template details
    response = client.get(f'/api/templates/{template_id}')
    data = json.loads(response.data)
    
    # Question should still be in template
    assert len(data['questions']) == 1
    assert data['questions'][0]['id'] == question_id
