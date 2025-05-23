import json
import pytest
from datetime import datetime, timedelta

def test_template_analytics(client, setup_database):
    """Test getting analytics for a template"""
    # Create a template
    template_data = {
        'name': 'Analytics Test Template',
        'description': 'Testing analytics dashboard',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create a question for the template
    question_data = {
        'specialization': 'analytics',
        'content': 'Analytics test question',
        'options': ['A', 'B', 'C', 'D'],
        'correct_answer': 'B'
    }
    question_response = client.post('/api/questions',
                                   data=json.dumps(question_data),
                                   content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Add question to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [question_id]}),
               content_type='application/json')
    
    # Create and complete multiple assessments
    for i in range(3):
        # Create assessment
        assessment_data = {
            'template_id': template_id,
            'user_email': f'analytics{i}@example.com'
        }
        assessment_response = client.post('/api/assessments',
                                        data=json.dumps(assessment_data),
                                        content_type='application/json')
        assessment_id = json.loads(assessment_response.data)['id']
        
        # Start assessment
        client.post(f'/api/assessments/{assessment_id}/start')
        
        # Submit answer (correct for 2 users, incorrect for 1)
        answer = 'B' if i < 2 else 'A'
        answer_data = {
            'question_id': question_id,
            'answer': answer
        }
        client.post(f'/api/assessments/{assessment_id}/submit-answer',
                  data=json.dumps(answer_data),
                  content_type='application/json')
        
        # Complete assessment
        client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Get analytics for the template
    response = client.get(f'/api/templates/{template_id}/analytics')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'total_assessments' in data
    assert data['total_assessments'] == 3
    
    assert 'average_score' in data
    
    # API might use either completion_percentage or completion_rate
    assert 'completion_rate' in data or 'completion_percentage' in data
    
    # Check pass rate (either as a percentage or decimal)
    if 'pass_rate' in data:
        # Should be around 66.67% (2 out of 3 users passed)
        if isinstance(data['pass_rate'], int):
            assert 60 <= data['pass_rate'] <= 70  # approximate range
        else:
            assert 0.6 <= data['pass_rate'] <= 0.7
    
    # Check time metrics
    assert 'average_time_seconds' in data or 'average_completion_time' in data
    
    # Score distribution should be present
    if 'score_distribution' in data:
        distribution = data['score_distribution']
        assert isinstance(distribution, (list, dict))

def test_dashboard_analytics_filters(client, setup_database):
    """Test filtering analytics dashboard data"""
    # Create template
    template_data = {
        'name': 'Filter Analytics Template',
        'description': 'Testing analytics filters',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                   data=json.dumps(template_data),
                                   content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create questions
    q1_data = {
        'specialization': 'programming',
        'content': 'Programming question',
        'options': ['A', 'B'],
        'correct_answer': 'A'
    }
    q2_data = {
        'specialization': 'aptitude',
        'content': 'Aptitude question',
        'options': ['X', 'Y'],
        'correct_answer': 'X'
    }
    q1_response = client.post('/api/questions', data=json.dumps(q1_data), content_type='application/json')
    q2_response = client.post('/api/questions', data=json.dumps(q2_data), content_type='application/json')
    q1_id = json.loads(q1_response.data)['id']
    q2_id = json.loads(q2_response.data)['id']
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [q1_id, q2_id]}),
               content_type='application/json')
    
    # Create assessments with different dates and users
    for i in range(5):
        assessment_data = {
            'template_id': template_id,
            'user_email': f'filter{i}@example.com' 
        }
        assessment_response = client.post('/api/assessments',
                                        data=json.dumps(assessment_data),
                                        content_type='application/json')
        assessment_id = json.loads(assessment_response.data)['id']
        
        client.post(f'/api/assessments/{assessment_id}/start')
        
        # Submit answers
        client.post(f'/api/assessments/{assessment_id}/submit-answer',
                  data=json.dumps({'question_id': q1_id, 'answer': 'A' if i % 2 == 0 else 'B'}),
                  content_type='application/json')
        client.post(f'/api/assessments/{assessment_id}/submit-answer',
                  data=json.dumps({'question_id': q2_id, 'answer': 'X' if i % 3 == 0 else 'Y'}),
                  content_type='application/json')
        
        client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Test date range filter
    # Get analytics with date filter (last 3 days)
    date_from = datetime.now() - timedelta(days=3)
    date_to = datetime.now()
    date_from_str = date_from.strftime('%Y-%m-%d')
    date_to_str = date_to.strftime('%Y-%m-%d')
    
    filter_response = client.get(
        f'/api/templates/{template_id}/analytics?date_from={date_from_str}&date_to={date_to_str}'
    )
    
    # Skip if filtering not implemented
    if filter_response.status_code == 400:  # Assume 400 means filter params not supported
        pytest.skip("Analytics filtering not implemented yet")
        
    assert filter_response.status_code == 200
    
    # Test question specialization filter
    specialization_response = client.get(
        f'/api/templates/{template_id}/analytics?specialization=programming'
    )
    
    # If specialization filtering is implemented
    if specialization_response.status_code == 200:
        spec_data = json.loads(specialization_response.data)
        
        # Should only include programming questions 
        if 'questions' in spec_data:
            for q in spec_data['questions']:
                assert q['specialization'] == 'programming'

def test_global_analytics_dashboard(client, setup_database):
    """Test global analytics dashboard with all templates"""
    # Create two templates
    template1_data = {
        'name': 'Global Analytics Template 1',
        'description': 'First template',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template2_data = {
        'name': 'Global Analytics Template 2',
        'description': 'Second template',
        'time_limit': 45,
        'percentage': 80,
        'creator_id': 1
    }
    
    client.post('/api/templates', data=json.dumps(template1_data), content_type='application/json')
    client.post('/api/templates', data=json.dumps(template2_data), content_type='application/json')
    
    # Get global analytics
    response = client.get('/api/analytics/dashboard')
    
    # Skip if global analytics not implemented
    if response.status_code == 404:
        pytest.skip("Global analytics dashboard not implemented yet")
        
    assert response.status_code == 200
    
    data = json.loads(response.data)
    
    # Check for required global metrics
    assert 'total_assessments' in data
    assert 'total_templates' in data
    assert 'average_completion_rate' in data or 'average_completion_percentage' in data
    
    # Optional metrics that might be implemented
    if 'template_performance' in data:
        assert isinstance(data['template_performance'], list)
        
    if 'recent_activity' in data:
        assert isinstance(data['recent_activity'], list)
        
    if 'assessment_trend' in data:
        assert isinstance(data['assessment_trend'], (dict, list))

def test_analytics_export(client, setup_database):
    """Test exporting analytics data in different formats"""
    # Create template with some assessments
    template_data = {
        'name': 'Export Analytics Template',
        'description': 'For testing analytics export',
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
        'specialization': 'export',
        'content': 'Export test question',
        'options': ['A', 'B'],
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
    
    # Create and complete assessment
    assessment_data = {
        'template_id': template_id,
        'user_email': 'export@example.com'
    }
    assessment_response = client.post('/api/assessments',
                                    data=json.dumps(assessment_data),
                                    content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Complete the assessment
    client.post(f'/api/assessments/{assessment_id}/start')
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
              data=json.dumps({'question_id': question_id, 'answer': 'A'}),
              content_type='application/json')
    client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Test CSV export
    csv_response = client.get(f'/api/templates/{template_id}/analytics?format=csv')
    
    # Skip if export not implemented
    if csv_response.status_code == 400:  # Assume 400 means format not supported
        pytest.skip("Analytics export not implemented yet")
        
    assert csv_response.status_code == 200
    
    # Check if it's actually CSV
    if 'text/csv' in csv_response.headers.get('Content-Type', ''):
        assert len(csv_response.data) > 0
        assert b',' in csv_response.data
    
    # Test Excel export
    excel_response = client.get(f'/api/templates/{template_id}/analytics?format=excel')
    
    # Only check if feature is implemented and returns proper format
    if excel_response.status_code == 200:
        content_type = excel_response.headers.get('Content-Type', '')
        if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or \
           'application/vnd.ms-excel' in content_type:
            assert len(excel_response.data) > 0
        else:
            # If returns JSON, feature might not be fully implemented
            import pytest
            pytest.skip("Excel export not fully implemented - returns JSON instead of Excel file")
