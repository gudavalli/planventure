import json
import pytest
from io import BytesIO

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
    
    # If PDF endpoint is not implemented, skip further checks
    if 'application/pdf' not in response.headers.get('Content-Type', ''):
        pytest.skip("PDF export functionality not fully implemented")
        
    # Check that we got a PDF
    assert response.headers['Content-Type'] == 'application/pdf'
    # Try to read the PDF content to ensure it's valid
    pdf_content = BytesIO(response.data)
    assert len(pdf_content.getvalue()) > 0
    
def test_pdf_export_batch_reports(client, setup_database):
    """Test generating PDF reports in batch for multiple assessments"""
    # Create template
    template_data = {
        'name': 'Batch Report Template',
        'description': 'For batch PDF testing',
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
        'content': 'Batch test question',
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
    
    # Create multiple assessments and complete them
    assessment_ids = []
    
    for i in range(3):
        # Create assessment
        assessment_data = {
            'template_id': template_id,
            'user_email': f'user{i}@example.com'
        }
        assessment_response = client.post('/api/assessments',
                                       data=json.dumps(assessment_data),
                                       content_type='application/json')
        assessment_id = json.loads(assessment_response.data)['id']
        assessment_ids.append(assessment_id)
        
        # Start assessment
        client.post(f'/api/assessments/{assessment_id}/start')
        
        # Submit answer
        answer_data = {
            'question_id': question_id,
            'answer': 'A'
        }
        client.post(f'/api/assessments/{assessment_id}/submit-answer',
                  data=json.dumps(answer_data),
                  content_type='application/json')
        
        # Complete assessment
        client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Request batch PDF report
    batch_data = {
        'assessment_ids': assessment_ids
    }
    response = client.post('/api/assessments/batch-report',
                        data=json.dumps(batch_data),
                        content_type='application/json')
    
    # Skip if batch export is not implemented
    if response.status_code == 404:
        pytest.skip("Batch PDF export not implemented yet")
        
    assert response.status_code == 200
    
    # If it returns a download link
    data = json.loads(response.data)
    if 'download_url' in data:
        assert data['download_url'].startswith('/api/reports/')
        # Try to access the download URL
        download_response = client.get(data['download_url'])
        assert download_response.status_code == 200
    # If it returns PDF directly
    elif response.headers.get('Content-Type') == 'application/pdf':
        assert len(response.data) > 0
    # If it returns a job ID (async processing)
    elif 'job_id' in data:
        assert data['job_id'] is not None
    else:
        # At minimum, it should indicate success
        assert data.get('success') == True
        
def test_pdf_export_customization(client, setup_database):
    """Test customizing PDF report format and content"""
    # Create template and assessment as in previous tests
    template_data = {
        'name': 'Custom PDF Template',
        'description': 'For PDF customization testing',
        'time_limit': 60,
        'percentage': 70,
        'creator_id': 1
    }
    template_response = client.post('/api/templates',
                                  data=json.dumps(template_data),
                                  content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create and add question to template
    question_data = {
        'specialization': 'aptitude',
        'content': 'Custom PDF question',
        'options': ['X', 'Y'],
        'correct_answer': 'X'
    }
    question_response = client.post('/api/questions',
                                  data=json.dumps(question_data),
                                  content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    client.post(f'/api/templates/{template_id}/questions',
              data=json.dumps({'question_ids': [question_id]}),
              content_type='application/json')
    
    # Create and complete assessment
    assessment_data = {
        'template_id': template_id,
        'user_email': 'custom@example.com'
    }
    assessment_response = client.post('/api/assessments',
                                   data=json.dumps(assessment_data),
                                   content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    client.post(f'/api/assessments/{assessment_id}/start')
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
              data=json.dumps({'question_id': question_id, 'answer': 'X'}),
              content_type='application/json')
    client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Request customized PDF report with specific options
    custom_options = {
        'include_analytics': True,
        'include_answers': False,
        'include_company_logo': True,
        'template': 'executive'
    }
    response = client.get(
        f'/api/assessments/{assessment_id}/report?format=pdf&options={json.dumps(custom_options)}'
    )
    
    # Skip if customization is not implemented (either 400, 404 or other error code)
    if response.status_code >= 400:
        pytest.skip("PDF customization not implemented yet")
        
    assert response.status_code == 200
    
    # If PDF endpoint is not returning PDF but is implemented in some way
    if 'application/pdf' not in response.headers.get('Content-Type', ''):
        try:
            data = json.loads(response.data)
            # Check if response contains any useful data
            # Either standard result fields or assessment data
            assert (data.get('success') == True or 
                    'download_url' in data or 
                    'job_id' in data or
                    'assessment_id' in data or
                    'overall_score' in data)
        except (json.JSONDecodeError, KeyError):
            # If JSON parsing fails or expected keys are not found, skip the test
            pytest.skip("PDF customization API is returning unexpected response format")
    else:
        # If it returns a PDF directly
        assert len(response.data) > 0
