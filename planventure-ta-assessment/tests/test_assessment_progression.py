import json
import pytest
from datetime import datetime
from models.assessment import AssessmentTemplate, Assessment, AssessmentResponse
from models.question import Question

def test_random_question_selection(client, setup_database):
    """Test that questions are randomly selected based on template percentage"""
    # Create a template
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template for Random Selection',
            'description': 'Test',
            'percentage': 50.0,  # Select 50% of questions
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create 10 questions
    question_ids = []
    for i in range(10):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i}',
            'options': ['1', '2', '3', '4'],
            'correct_answer': '2'
        }
        question_response = client.post('/api/questions',
                                    data=json.dumps(question_data),
                                    content_type='application/json')
        question_ids.append(json.loads(question_response.data)['id'])
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
                data=json.dumps({'question_ids': question_ids}),
                content_type='application/json')
    
    # Create assessment
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Start assessment
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Get selected questions
    response = client.get(f'/api/assessments/{assessment_id}/questions')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    # Should have 5 questions (50% of 10)
    assert len(data['questions']) == 5
    # Verify questions are from the template
    assert all(q['id'] in question_ids for q in data['questions'])

def test_time_limit_tracking(client, setup_database):
    """Test assessment time limit tracking"""
    # Create template with time limit
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Template with Time Limit',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 30,  # 30 minutes
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create assessment
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Start assessment
    start_response = client.post(f'/api/assessments/{assessment_id}/start')
    assert start_response.status_code == 200
    data = json.loads(start_response.data)
    
    assert 'start_time' in data
    assert 'time_remaining' in data
    assert data['time_remaining'] <= 30 * 60  # Time in seconds

def test_sequential_question_progression(client, setup_database):
    """Test questions are presented sequentially"""
    # Create template
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Sequential Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create questions
    questions = []
    for i in range(3):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i}',
            'options': ['1', '2', '3', '4'],
            'correct_answer': '2'
        }
        response = client.post('/api/questions',
                           data=json.dumps(question_data),
                           content_type='application/json')
        questions.append(json.loads(response.data))
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [q['id'] for q in questions]}),
               content_type='application/json')
    
    # Create and start assessment
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Get first question
    response = client.get(f'/api/assessments/{assessment_id}/current-question')
    data = json.loads(response.data)
    assert data['question']['content'] == 'Question 0'
    
    # Submit answer and move to next question
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
               data=json.dumps({
                   'question_id': data['question']['id'],
                   'answer': '2'
               }),
               content_type='application/json')
    
    # Get next question
    response = client.get(f'/api/assessments/{assessment_id}/current-question')
    data = json.loads(response.data)
    assert data['question']['content'] == 'Question 1'

def test_score_calculation(client, setup_database):
    """Test assessment score calculation"""
    # Create template
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Scoring Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create questions
    questions = []
    correct_answers = ['2', '3', '1']
    for i, answer in enumerate(correct_answers):
        question_data = {
            'specialization': 'aptitude',
            'content': f'Question {i}',
            'options': ['1', '2', '3', '4'],
            'correct_answer': answer
        }
        response = client.post('/api/questions',
                           data=json.dumps(question_data),
                           content_type='application/json')
        questions.append(json.loads(response.data))
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [q['id'] for q in questions]}),
               content_type='application/json')
    
    # Create and start assessment
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Submit answers (2 correct, 1 wrong)
    user_answers = ['2', '3', '2']  # Last answer is wrong
    for i, (question, answer) in enumerate(zip(questions, user_answers)):
        response = client.post(f'/api/assessments/{assessment_id}/submit-answer',
                            data=json.dumps({
                                'question_id': question['id'],
                                'answer': answer
                            }),
                            content_type='application/json')
        assert response.status_code == 200
    
    # Complete assessment
    response = client.post(f'/api/assessments/{assessment_id}/complete')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify score (2 correct out of 3 = 66.67%)
    assert data['total_score'] == pytest.approx(66.67, rel=0.01)

def test_detailed_response_report(client, setup_database):
    """Test generating detailed response report"""
    # Create and complete an assessment with mixed responses
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Report Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create different types of questions
    questions = []
    # Aptitude question
    response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'aptitude',
            'content': 'Math Question',
            'options': ['1', '2', '3', '4'],
            'correct_answer': '2'
        }),
        content_type='application/json')
    questions.append(json.loads(response.data))
    
    # Reading comprehension set
    set_response = client.post('/api/reading-sets',
        data=json.dumps({
            'paragraph': 'Sample paragraph for comprehension.',
            'specialization': 'reading_comprehension'
        }),
        content_type='application/json')
    reading_set_id = json.loads(set_response.data)['id']
    
    response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'reading_comprehension',
            'content': 'Comprehension Question',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'B',
            'reading_set_id': reading_set_id
        }),
        content_type='application/json')
    questions.append(json.loads(response.data))
    
    # Typing question
    response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'typing',
            'content': 'The quick brown fox jumps over the lazy dog.',
        }),
        content_type='application/json')
    questions.append(json.loads(response.data))
    
    # Add questions to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [q['id'] for q in questions]}),
               content_type='application/json')
    
    # Create and start assessment
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': 'test@example.com'
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    client.post(f'/api/assessments/{assessment_id}/start')
    
    # Submit answers for all question types
    # Aptitude - correct
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
               data=json.dumps({
                   'question_id': questions[0]['id'],
                   'answer': '2'
               }),
               content_type='application/json')
    
    # Reading comprehension - incorrect
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
               data=json.dumps({
                   'question_id': questions[1]['id'],
                   'answer': 'C'
               }),
               content_type='application/json')
    
    # Typing - partial accuracy
    client.post(f'/api/assessments/{assessment_id}/submit-answer',
               data=json.dumps({
                   'question_id': questions[2]['id'],
                   'answer': 'The quick brwn fox jumps over the lasy dog.',
                   'typing_metrics': {
                       'accuracy': 90.0,
                       'wpm': 45
                   }
               }),
               content_type='application/json')
    
    # Complete assessment
    client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Get detailed report
    response = client.get(f'/api/assessments/{assessment_id}/report')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify report structure and content
    assert 'overall_score' in data
    assert 'section_scores' in data
    assert 'question_details' in data
    assert 'time_taken' in data
    
    # Verify section scores
    assert 'aptitude' in data['section_scores']
    assert 'reading_comprehension' in data['section_scores']
    assert 'typing' in data['section_scores']
    
    # Verify question details
    assert len(data['question_details']) == 3
    assert any(q['specialization'] == 'aptitude' for q in data['question_details'])
    assert any(q['specialization'] == 'reading_comprehension' for q in data['question_details'])
    assert any(q['specialization'] == 'typing' for q in data['question_details'])

def test_email_verification_and_link_access(client, setup_database):
    """Test email verification and assessment link access"""
    # Create template and assessment
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Email Test Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    user_email = 'candidate@example.com'
    assessment_response = client.post('/api/assessments',
        data=json.dumps({
            'template_id': template_id,
            'user_email': user_email
        }),
        content_type='application/json')
    assessment_id = json.loads(assessment_response.data)['id']
    
    # Verify assessment link is generated
    response = client.get(f'/api/assessments/{assessment_id}')
    data = json.loads(response.data)
    assert 'access_url' in data
    
    # Simulate email verification
    access_token = data['access_url'].split('token=')[1]
    response = client.post('/api/verify-email',
                        data=json.dumps({
                            'email': user_email,
                            'token': access_token
                        }),
                        content_type='application/json')
    assert response.status_code == 200
    
    # Access assessment with verified email
    response = client.get(f'/api/assessments/{assessment_id}/access',
                       headers={'X-User-Email': user_email,
                              'X-Access-Token': access_token})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'pending'

def test_admin_analytics_report(client, setup_database):
    """Test admin analytics report generation"""
    # Create template with multiple assessments and responses
    template_response = client.post('/api/templates',
        data=json.dumps({
            'name': 'Analytics Template',
            'description': 'Test',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }),
        content_type='application/json')
    template_id = json.loads(template_response.data)['id']
    
    # Create a question
    question_response = client.post('/api/questions',
        data=json.dumps({
            'specialization': 'aptitude',
            'content': 'Test Question',
            'options': ['1', '2', '3', '4'],
            'correct_answer': '2'
        }),
        content_type='application/json')
    question_id = json.loads(question_response.data)['id']
    
    # Add question to template
    client.post(f'/api/templates/{template_id}/questions',
               data=json.dumps({'question_ids': [question_id]}),
               content_type='application/json')
    
    # Create multiple assessments and submit responses
    for i in range(5):
        assessment_response = client.post('/api/assessments',
            data=json.dumps({
                'template_id': template_id,
                'user_email': f'user{i}@example.com'
            }),
            content_type='application/json')
        assessment_id = json.loads(assessment_response.data)['id']
        
        # Start assessment
        client.post(f'/api/assessments/{assessment_id}/start')
        
        # Submit answer (alternate correct/incorrect)
        client.post(f'/api/assessments/{assessment_id}/submit-answer',
                   data=json.dumps({
                       'question_id': question_id,
                       'answer': '2' if i % 2 == 0 else '1'
                   }),
                   content_type='application/json')
        
        # Complete assessment
        client.post(f'/api/assessments/{assessment_id}/complete')
    
    # Get analytics report
    response = client.get(f'/api/templates/{template_id}/analytics')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify analytics data    assert 'total_assessments' in data
    assert data['total_assessments'] == 5
    assert 'average_score' in data
    assert 'completion_rate' in data
    assert 'average_time_seconds' in data
    assert 'question_stats' in data
    
    # Verify question statistics
    question_stats = data['question_stats']
    assert any(q['id'] == question_id for q in question_stats)
    stats = next(q for q in question_stats if q['id'] == question_id)
    assert stats['correct_percentage'] == pytest.approx(60.0, rel=0.01)  # 3 out of 5 correct
