"""
Unit tests for the DELETE endpoint and assessment template management.
Tests the remove_question_from_template functionality and related operations.
"""

import json
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.assessment import AssessmentTemplate
from models.question import Question
from models.database import db


class TestDeleteEndpoint:
    """Test suite for the DELETE question from template endpoint."""

    def test_remove_question_from_template_success(self, client):
        """Test successfully removing a question from a template."""
        # Create a template
        template_data = {
            'name': 'Test Template for Deletion',
            'description': 'Testing deletion functionality',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create a question
        question_data = {
            'specialization': 'programming',
            'content': 'What is Python?',
            'options': ['A programming language', 'A snake', 'A tool', 'An animal'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'medium'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Add question to template
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': [question_id]}),
                                 content_type='application/json')
        assert add_response.status_code == 200

        # Verify question was added (template should have 1 question)
        template_details_response = client.get(f'/api/templates/{template_id}')
        assert template_details_response.status_code == 200
        template_details = json.loads(template_details_response.data)
        assert template_details['question_count'] == 1

        # Remove question from template
        delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
        assert delete_response.status_code == 200
        
        delete_data = json.loads(delete_response.data)
        assert delete_data['message'] == 'Question removed from template successfully'
        assert delete_data['template_id'] == template_id
        assert delete_data['question_id'] == question_id
        assert delete_data['remaining_questions'] == 0

        # Verify question was removed (template should have 0 questions)
        template_details_response = client.get(f'/api/templates/{template_id}')
        assert template_details_response.status_code == 200
        template_details = json.loads(template_details_response.data)
        assert template_details['question_count'] == 0

    def test_remove_question_template_not_found(self, client):
        """Test removing a question from a non-existent template."""
        non_existent_template_id = 99999
        question_id = 1
        
        response = client.delete(f'/api/templates/{non_existent_template_id}/questions/{question_id}')
        assert response.status_code == 404
        
        error_data = json.loads(response.data)
        assert error_data['error'] == 'Template or question not found'

    def test_remove_question_question_not_found(self, client):
        """Test removing a non-existent question from a template."""
        # Create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Testing with non-existent question',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        non_existent_question_id = 99999
        response = client.delete(f'/api/templates/{template_id}/questions/{non_existent_question_id}')
        assert response.status_code == 404
        
        error_data = json.loads(response.data)
        assert error_data['error'] == 'Template or question not found'

    def test_remove_question_not_associated_with_template(self, client):
        """Test removing a question that is not associated with the template."""
        # Create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Testing unassociated question',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create a question but don't add it to the template
        question_data = {
            'specialization': 'programming',
            'content': 'What is JavaScript?',
            'options': ['A language', 'A script', 'A tool', 'A framework'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'easy'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Try to remove the question from the template (should fail)
        response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
        assert response.status_code == 400
        
        error_data = json.loads(response.data)
        assert error_data['error'] == 'Question is not associated with this template'

    def test_remove_multiple_questions_from_template(self, client):
        """Test removing multiple questions one by one from a template."""
        # Create a template
        template_data = {
            'name': 'Multi-Question Template',
            'description': 'Testing multiple question removal',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create multiple questions
        question_ids = []
        for i in range(3):
            question_data = {
                'specialization': 'test',
                'content': f'Question {i + 1}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'medium'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            assert question_response.status_code == 201
            question_ids.append(json.loads(question_response.data)['id'])

        # Add all questions to template
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': question_ids}),
                                 content_type='application/json')
        assert add_response.status_code == 200

        # Verify all questions were added
        template_details_response = client.get(f'/api/templates/{template_id}')
        assert template_details_response.status_code == 200
        template_details = json.loads(template_details_response.data)
        assert template_details['question_count'] == 3

        # Remove questions one by one
        for i, question_id in enumerate(question_ids):
            expected_remaining = len(question_ids) - i - 1
            
            delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
            assert delete_response.status_code == 200
            
            delete_data = json.loads(delete_response.data)
            assert delete_data['remaining_questions'] == expected_remaining

        # Verify all questions were removed
        template_details_response = client.get(f'/api/templates/{template_id}')
        assert template_details_response.status_code == 200
        template_details = json.loads(template_details_response.data)
        assert template_details['question_count'] == 0


class TestTemplateDetailsEndpoint:
    """Test suite for the GET template details endpoint."""

    def test_get_template_details_success(self, client):
        """Test successfully retrieving template details."""
        # Create a template
        template_data = {
            'name': 'Details Test Template',
            'description': 'Testing template details retrieval',
            'percentage': 75.0,
            'time_limit': 45,
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Get template details
        response = client.get(f'/api/templates/{template_id}')
        assert response.status_code == 200
        
        details = json.loads(response.data)
        assert details['id'] == template_id
        assert details['name'] == 'Details Test Template'
        assert details['description'] == 'Testing template details retrieval'
        assert details['percentage'] == 75.0
        assert details['time_limit'] == 45
        assert details['creator_id'] == 1
        assert details['question_count'] == 0
        assert 'created_at' in details

    def test_get_template_details_with_questions(self, client):
        """Test retrieving template details when template has questions."""
        # Create a template
        template_data = {
            'name': 'Template with Questions',
            'description': 'Testing template with questions',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create and add questions
        question_ids = []
        for i in range(2):
            question_data = {
                'specialization': 'test',
                'content': f'Sample Question {i + 1}?',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'easy'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            assert question_response.status_code == 201
            question_ids.append(json.loads(question_response.data)['id'])

        # Add questions to template
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': question_ids}),
                                 content_type='application/json')
        assert add_response.status_code == 200

        # Get template details
        response = client.get(f'/api/templates/{template_id}')
        assert response.status_code == 200
        
        details = json.loads(response.data)
        assert details['question_count'] == 2

    def test_get_template_details_not_found(self, client):
        """Test retrieving details for a non-existent template."""
        non_existent_id = 99999
        response = client.get(f'/api/templates/{non_existent_id}')
        assert response.status_code == 404


class TestAssessmentTemplateIntegration:
    """Integration tests for assessment template operations."""

    def test_full_template_lifecycle(self, client):
        """Test the complete lifecycle of a template: create, add questions, remove questions, delete."""
        # Create template
        template_data = {
            'name': 'Lifecycle Test Template',
            'description': 'Testing full lifecycle',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create questions
        question_ids = []
        for i in range(3):
            question_data = {
                'specialization': 'lifecycle',
                'content': f'Lifecycle Question {i + 1}?',
                'options': ['Answer 1', 'Answer 2', 'Answer 3', 'Answer 4'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'medium'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            assert question_response.status_code == 201
            question_ids.append(json.loads(question_response.data)['id'])

        # Add questions to template
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': question_ids}),
                                 content_type='application/json')
        assert add_response.status_code == 200

        # Verify questions were added
        details_response = client.get(f'/api/templates/{template_id}')
        assert details_response.status_code == 200
        details = json.loads(details_response.data)
        assert details['question_count'] == 3

        # Remove one question
        delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_ids[0]}')
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.data)
        assert delete_data['remaining_questions'] == 2

        # Verify question was removed
        details_response = client.get(f'/api/templates/{template_id}')
        assert details_response.status_code == 200
        details = json.loads(details_response.data)
        assert details['question_count'] == 2

        # Try to remove the same question again (should fail)
        delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_ids[0]}')
        assert delete_response.status_code == 400
        error_data = json.loads(delete_response.data)
        assert error_data['error'] == 'Question is not associated with this template'

    def test_concurrent_question_operations(self, client):
        """Test handling multiple operations on the same template."""
        # Create template
        template_data = {
            'name': 'Concurrent Operations Template',
            'description': 'Testing concurrent operations',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create multiple questions
        question_ids = []
        for i in range(5):
            question_data = {
                'specialization': 'concurrent',
                'content': f'Concurrent Question {i + 1}?',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'hard'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            assert question_response.status_code == 201
            question_ids.append(json.loads(question_response.data)['id'])

        # Add questions in batches
        batch1 = question_ids[:3]
        batch2 = question_ids[3:]

        # Add first batch
        add_response1 = client.post(f'/api/templates/{template_id}/questions',
                                  data=json.dumps({'question_ids': batch1}),
                                  content_type='application/json')
        assert add_response1.status_code == 200

        # Add second batch
        add_response2 = client.post(f'/api/templates/{template_id}/questions',
                                  data=json.dumps({'question_ids': batch2}),
                                  content_type='application/json')
        assert add_response2.status_code == 200

        # Verify all questions were added
        details_response = client.get(f'/api/templates/{template_id}')
        assert details_response.status_code == 200
        details = json.loads(details_response.data)
        assert details['question_count'] == 5

        # Remove questions from different batches
        delete_response1 = client.delete(f'/api/templates/{template_id}/questions/{batch1[0]}')
        assert delete_response1.status_code == 200

        delete_response2 = client.delete(f'/api/templates/{template_id}/questions/{batch2[0]}')
        assert delete_response2.status_code == 200

        # Verify correct number of questions remain
        details_response = client.get(f'/api/templates/{template_id}')
        assert details_response.status_code == 200
        details = json.loads(details_response.data)
        assert details['question_count'] == 3
