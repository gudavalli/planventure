import json
import pytest
from datetime import datetime
from models.assessment import AssessmentTemplate, Assessment

def test_create_template(client, setup_database):
    """Test creating a new assessment template"""
    data = {
        'name': 'Test Template',
        'description': 'Test Description',
        'percentage': 80.0,
        'time_limit': 60,
        'creator_id': 1
    }
    response = client.post('/api/templates',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_create_template_invalid_data(client, setup_database):
    """Test creating a template with missing required fields"""
    data = {
        'description': 'Test Description'  # Missing name and creator_id
    }
    response = client.post('/api/templates',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert 'error' in response_data
    assert 'missing_fields' in response_data
    assert set(response_data['missing_fields']) == {'name', 'creator_id'}

def test_add_questions_to_template(client, setup_database):
    """Test adding questions to a template"""
    # Create a template first
    template_data = {
        'name': 'Test Template',
        'description': 'Test Description',
        'percentage': 100.0,
        'time_limit': 60,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                 data=json.dumps(template_data),
                                 content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create some questions
    question_ids = []
    for i in range(2):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i}',
            'options': ['1', '2'],
            'correct_answer': '2'
        }
        question_response = client.post('/api/questions',
                                     data=json.dumps(question_data),
                                     content_type='application/json')
        question_ids.append(json.loads(question_response.data)['id'])
    
    # Add questions to template
    response = client.post(f'/api/templates/{template_id}/questions',
                         data=json.dumps({'question_ids': question_ids}),
                         content_type='application/json')
    
    assert response.status_code == 200

def test_create_assessment(client, setup_database):
    """Test creating a new assessment"""
    # Create a template first
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template for Assessment',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create an assessment
    assessment_data = {
        'template_id': template_id,
        'user_email': 'test@example.com'
    }
    response = client.post('/api/assessments',
                         data=json.dumps(assessment_data),
                         content_type='application/json')
    
    assert response.status_code == 201
    assert 'id' in json.loads(response.data)

def test_start_assessment(client, setup_database):
    """Test starting an assessment"""
    # Create template and assessment first
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Start the assessment
    response = client.post(f'/api/assessments/{assessment_id}/start')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'start_time' in data
    
def test_start_assessment_already_started(client, setup_database):
    """Test starting an already started assessment"""
    # Create and start an assessment
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Start the assessment first time
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Try to start it again
    response = client.post(f'/api/assessments/{assessment_id}/start')
    assert response.status_code == 400

def test_list_templates(client, setup_database):
    """Test listing assessment templates"""
    # Create some templates first
    templates = []
    for i in range(3):
        data = {
            'name': f'Template {i}',
            'description': f'Description {i}',
            'percentage': 80.0,
            'time_limit': 60,
            'creator_id': 1
        }
        response = client.post('/api/templates',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 201
        templates.append(json.loads(response.data))
    
    # Get list of templates
    response = client.get('/api/templates')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'templates' in data
    assert 'pagination' in data
    assert len(data['templates']) == 3
    assert all('id' in t for t in data['templates'])
    assert all('name' in t for t in data['templates'])
    assert all('description' in t for t in data['templates'])
    assert all('question_count' in t for t in data['templates'])

def test_list_templates_pagination(client, setup_database):
    """Test template listing with pagination and filters"""
    # Create more than one page of templates
    templates = []
    for i in range(15):  # Create 15 templates (more than default per_page)
        data = {
            'name': f'Template {i}',
            'description': f'Description {i}',
            'percentage': 80.0,
            'time_limit': 60,
            'creator_id': 1
        }
        response = client.post('/api/templates',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 201
        templates.append(json.loads(response.data))
    
    # Test default pagination (page 1, per_page 10)
    response = client.get('/api/templates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['templates']) == 10  # Default per_page
    assert data['pagination']['total_items'] == 15
    assert data['pagination']['total_pages'] == 2
    assert data['pagination']['has_next'] is True
    
    # Test second page
    response = client.get('/api/templates?page=2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['templates']) == 5  # Remaining items
    assert data['pagination']['current_page'] == 2
    assert data['pagination']['has_next'] is False
    
    # Test search filter
    response = client.get('/api/templates?search=Template 1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all('Template 1' in t['name'] for t in data['templates'])
    
    # Test custom per_page
    response = client.get('/api/templates?per_page=5')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['templates']) == 5
    assert data['pagination']['total_pages'] == 3

def test_list_assessments(client, setup_database):
    """Test listing assessments"""
    # Create a template first
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template for Assessment List',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create multiple assessments
    assessments = []
    for i in range(3):
        data = {
            'template_id': template_id,
            'user_email': f'test{i}@example.com'
        }
        response = client.post('/api/assessments',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 201
        assessments.append(json.loads(response.data))
    
    # Get all assessments
    response = client.get('/api/assessments')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'assessments' in data
    assert 'pagination' in data
    assert len(data['assessments']) == 3
    
    # Filter by user_email
    response = client.get('/api/assessments?user_email=test0@example.com')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['assessments']) == 1
    assert data['assessments'][0]['user_email'] == 'test0@example.com'

def test_list_assessments_pagination(client, setup_database):
    """Test assessment listing with pagination and filters"""
    # Create a template first
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template for Pagination Test',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create more than one page of assessments
    assessments = []
    for i in range(15):  # Create 15 assessments (more than default per_page)
        data = {
            'template_id': template_id,
            'user_email': f'test{i}@example.com'
        }
        response = client.post('/api/assessments',
                            data=json.dumps(data),
                            content_type='application/json')
        assert response.status_code == 201
        assessments.append(json.loads(response.data))
        
        # Start some assessments to test status filter
        if i % 2 == 0:
            client.post(f'/api/assessments/{json.loads(response.data)["id"]}/start')
    
    # Test default pagination (page 1, per_page 10)
    response = client.get('/api/assessments')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['assessments']) == 10  # Default per_page
    assert data['pagination']['total_items'] == 15
    assert data['pagination']['total_pages'] == 2
    assert data['pagination']['has_next'] is True
    
    # Test status filter
    response = client.get('/api/assessments?status=in_progress')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(a['status'] == 'in_progress' for a in data['assessments'])
    
    # Test user_email filter
    response = client.get('/api/assessments?user_email=test0@example.com')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(a['user_email'] == 'test0@example.com' for a in data['assessments'])
    
    # Test template_id filter
    response = client.get(f'/api/assessments?template_id={template_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(a['template_id'] == template_id for a in data['assessments'])
