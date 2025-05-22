import json
import pytest
from datetime import datetime, timedelta

def test_templates_pagination(client, setup_database):
    """Test pagination for templates API"""
    # Create multiple templates
    for i in range(15):  # Create 15 templates
        template_data = {
            'name': f'Template {i}',
            'description': f'Description {i}',
            'time_limit': 60,
            'percentage': 70,
            'creator_id': 1
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
        'percentage': 70,
        'creator_id': 1
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
        'percentage': 70,
        'creator_id': 1
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

def test_questions_pagination(client, setup_database):
    """Test pagination for questions API"""
    # Add multiple questions
    for i in range(15):  # Create 15 questions
        client.post('/api/questions',
            data=json.dumps({
                'specialization': 'aptitude',
                'content': f'Question {i}',
                'options': ['1', '2'],
                'correct_answer': '2'
            }),
            content_type='application/json')
    
    # Test first page (default 10 per page)
    response = client.get('/api/questions')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['questions']) == 10
    assert data['pagination']['total'] == 15
    assert data['pagination']['page'] == 1
    
    # Test second page
    response = client.get('/api/questions?page=2')
    data = json.loads(response.data)
    
    assert len(data['questions']) == 5
    assert data['pagination']['page'] == 2
    
    # Test with custom per_page parameter
    response = client.get('/api/questions?per_page=5')
    data = json.loads(response.data)
    
    assert len(data['questions']) == 5
    assert data['pagination']['total_pages'] == 3

def test_pdf_export_assessment_report(client, setup_database):
    """Test getting assessment report with PDF format option"""
    # Create template with question
    template_data = {
        'name': 'PDF Export Template',
        'description': 'For PDF export testing',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create question
    question_data = {
        'specialization': 'aptitude',
        'content': 'PDF export test question',
        'options': ['1', '2'],
        'correct_answer': '2'
    }
    question_response = client.post('/api/questions',
                                   data=json.dumps(question_data),
                                   content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Add question to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [question_id]}),
               content_type='application/json')
    
    # Create assessment
    assessment_data = {
        'template_id': template_id,
        'user_email': 'candidate@example.com'
    }
    assessment_response = client.post('/api/assessments',
                                    data=json.dumps(assessment_data),
                                    content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Start assessment
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Submit answer
    answer_data = {
        'question_id': question_id,
        'answer': '2'
    }
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
               data=json.dumps(answer_data),
               content_type='application/json')
    
    # Complete assessment
    client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Request PDF report
    response = client.get(f'/api/assessments/{assessment_id}/report?format=pdf')
    
    # We might not actually generate a PDF in tests, but API should accept the format parameter
    assert response.status_code == 200
    # If PDF is actually generated:
    # assert response.headers['Content-Type'] == 'application/pdf'
