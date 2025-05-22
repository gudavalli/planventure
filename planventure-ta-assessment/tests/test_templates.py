import json
import pytest
from models.assessment import Template

def test_create_template(client, setup_database):
    """Test creating a new assessment template"""
    data = {
        'name': 'Technical Interview',
        'description': 'Assessment for technical skills',
        'time_limit': 60,  # minutes
        'percentage': 70  # passing percentage
    }
    response = client.post('/api/templates',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_get_templates(client, setup_database):
    """Test getting all templates"""
    # Create test templates
    template1 = {
        'name': 'Technical Interview',
        'description': 'Technical skills assessment',
        'time_limit': 60,
        'percentage': 70
    }
    template2 = {
        'name': 'Typing Test',
        'description': 'Typing speed assessment',
        'time_limit': 30,
        'percentage': 60
    }
    
    client.post('/api/templates',
               data=json.dumps(template1),
               content_type='application/json')
    client.post('/api/templates',
               data=json.dumps(template2),
               content_type='application/json')
    
    response = client.get('/api/templates')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'templates' in data
    assert len(data['templates']) == 2
    assert 'pagination' in data

def test_get_template_details(client, setup_database):
    """Test getting a specific template with its questions"""
    # Create a template
    template_data = {
        'name': 'Technical Interview',
        'description': 'Assessment for technical skills',
        'time_limit': 60,
        'percentage': 70
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create a question
    question_data = {
        'specialization': 'aptitude',
        'content': 'What is 2+2?',
        'options': ['3', '4', '5', '6'],
        'correct_answer': '4'
    }
    question_response = client.post('/api/questions',
                                   data=json.dumps(question_data),
                                   content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Add question to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [question_id]}),
               content_type='application/json')
    
    # Get template details
    response = client.get(f'/api/templates/{template_id}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['name'] == 'Technical Interview'
    assert 'questions' in data
    assert len(data['questions']) == 1
    assert data['questions'][0]['content'] == 'What is 2+2?'

def test_templates_pagination(client, setup_database):
    """Test pagination for templates API"""
    # Create multiple templates
    for i in range(15):  # Create 15 templates
        template_data = {
            'name': f'Template {i}',
            'description': f'Description {i}',
            'time_limit': 60,
            'percentage': 70
        }
        client.post('/api/templates',
                   data=json.dumps(template_data),
                   content_type='application/json')
    
    # Test first page (default 10 per page)
    response = client.get('/api/templates')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['templates']) == 10
    assert data['pagination']['total'] == 15
    assert data['pagination']['page'] == 1
    
    # Test second page
    response = client.get('/api/templates?page=2')
    data = json.loads(response.data)
    
    assert len(data['templates']) == 5
    assert data['pagination']['page'] == 2
    
    # Test with custom per_page parameter
    response = client.get('/api/templates?per_page=5')
    data = json.loads(response.data)
    
    assert len(data['templates']) == 5
    assert data['pagination']['total_pages'] == 3

def test_clone_template(client, setup_database):
    """Test cloning a template with its questions"""
    # Create original template
    template_data = {
        'name': 'Original Template',
        'description': 'Template to clone',
        'time_limit': 60,
        'percentage': 70
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Add questions to the template
    # First create questions
    questions = []
    for i in range(3):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i}',
            'options': ['1', '2', '3', '4'],
            'correct_answer': '2'
        }
        question_response = client.post('/api/questions',
                                       data=json.dumps(question_data),
                                       content_type='application/json')
        questions.append(json.loads(question_response.data)['id'])
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': questions}),
               content_type='application/json')
    
    # Clone the template
    clone_data = {
        'name': 'Cloned Template'
    }
    clone_response = client.post(f'/api/templates/{template_id}/clone',
                                data=json.dumps(clone_data),
                                content_type='application/json')
    
    assert clone_response.status_code == 201
    cloned_template_id = json.loads(clone_response.data)['id']
    
    # Get cloned template details
    response = client.get(f'/api/templates/{cloned_template_id}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['name'] == 'Cloned Template'
    assert data['description'] == 'Template to clone'
    assert data['time_limit'] == 60
    assert data['percentage'] == 70
    assert len(data['questions']) == 3

def test_template_analytics(client, setup_database):
    """Test getting analytics for a template"""
    # Create a template
    template_data = {
        'name': 'Analytics Test Template',
        'description': 'Testing analytics',
        'time_limit': 60,
        'percentage': 70
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Get analytics (even with no assessments, should return empty stats)
    response = client.get(f'/api/templates/{template_id}/analytics')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'total_assessments' in data
    assert 'average_score' in data
    assert 'completion_percentage' in data
    assert 'pass_rate' in data
    assert 'average_completion_time' in data
    assert 'score_distribution' in data
    
    # The test could be expanded with creating assessments and checking analytics
    # but that would require more complex setup with completed assessments
