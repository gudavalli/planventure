"""
Comprehensive error handling tests for the assessment template management system.
Tests various edge cases and error conditions for the DELETE endpoint and related functionality.
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


class TestErrorHandlingComprehensive:
    """Comprehensive error handling test suite."""

    def test_delete_with_invalid_template_id_format(self, client):
        """Test DELETE with invalid template ID format."""
        invalid_id = "not_a_number"
        question_id = 1
        
        response = client.delete(f'/api/templates/{invalid_id}/questions/{question_id}')
        # Flask typically converts non-numeric IDs, so this might still work
        # but the template won't be found
        assert response.status_code in [404, 400]

    def test_delete_with_invalid_question_id_format(self, client):
        """Test DELETE with invalid question ID format."""
        template_id = 1
        invalid_id = "not_a_number"
        
        response = client.delete(f'/api/templates/{template_id}/questions/{invalid_id}')
        assert response.status_code in [404, 400]

    def test_delete_with_negative_template_id(self, client):
        """Test DELETE with negative template ID."""
        negative_id = -1
        question_id = 1
        
        response = client.delete(f'/api/templates/{negative_id}/questions/{question_id}')
        assert response.status_code == 404

    def test_delete_with_negative_question_id(self, client):
        """Test DELETE with negative question ID."""
        template_id = 1
        negative_id = -1
        
        response = client.delete(f'/api/templates/{template_id}/questions/{negative_id}')
        assert response.status_code == 404

    def test_delete_with_zero_ids(self, client):
        """Test DELETE with zero IDs."""
        response = client.delete('/api/templates/0/questions/0')
        assert response.status_code == 404

    def test_template_details_with_large_id(self, client):
        """Test template details retrieval with very large ID."""
        large_id = 999999999999999999
        response = client.get(f'/api/templates/{large_id}')
        assert response.status_code == 404

    def test_concurrent_delete_operations(self, client):
        """Test multiple delete operations on the same template/question."""
        # Create a template
        template_data = {
            'name': 'Concurrent Test Template',
            'description': 'Testing concurrent operations',
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
            'content': 'Concurrent test question?',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 0,
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

        # First delete should succeed
        delete_response1 = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
        assert delete_response1.status_code == 200

        # Second delete should fail (question already removed)
        delete_response2 = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
        assert delete_response2.status_code == 400
        error_data = json.loads(delete_response2.data)
        assert error_data['error'] == 'Question is not associated with this template'

    def test_delete_question_from_multiple_templates(self, client):
        """Test removing the same question from multiple templates."""
        # Create two templates
        template_data1 = {
            'name': 'Template 1',
            'description': 'First template',
            'creator_id': 1
        }
        template_response1 = client.post('/api/templates',
                                       data=json.dumps(template_data1),
                                       content_type='application/json')
        assert template_response1.status_code == 201
        template_id1 = json.loads(template_response1.data)['id']

        template_data2 = {
            'name': 'Template 2',
            'description': 'Second template',
            'creator_id': 1
        }
        template_response2 = client.post('/api/templates',
                                       data=json.dumps(template_data2),
                                       content_type='application/json')
        assert template_response2.status_code == 201
        template_id2 = json.loads(template_response2.data)['id']

        # Create a question
        question_data = {
            'specialization': 'programming',
            'content': 'Shared question across templates?',
            'options': ['Yes', 'No', 'Maybe', 'Sometimes'],
            'correct_answer': 0,
            'difficulty': 'easy'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Add question to both templates
        add_response1 = client.post(f'/api/templates/{template_id1}/questions',
                                  data=json.dumps({'question_ids': [question_id]}),
                                  content_type='application/json')
        assert add_response1.status_code == 200

        add_response2 = client.post(f'/api/templates/{template_id2}/questions',
                                  data=json.dumps({'question_ids': [question_id]}),
                                  content_type='application/json')
        assert add_response2.status_code == 200

        # Remove question from first template
        delete_response1 = client.delete(f'/api/templates/{template_id1}/questions/{question_id}')
        assert delete_response1.status_code == 200

        # Question should still be in second template
        template_details = client.get(f'/api/templates/{template_id2}')
        assert template_details.status_code == 200
        details = json.loads(template_details.data)
        assert details['question_count'] == 1

        # Remove question from second template
        delete_response2 = client.delete(f'/api/templates/{template_id2}/questions/{question_id}')
        assert delete_response2.status_code == 200

    def test_template_question_count_consistency(self, client):
        """Test that question count remains consistent after operations."""
        # Create a template
        template_data = {
            'name': 'Consistency Test Template',
            'description': 'Testing question count consistency',
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
                'specialization': 'programming',
                'content': f'Test question {i+1}?',
                'options': [f'Option A{i}', f'Option B{i}', f'Option C{i}', f'Option D{i}'],
                'correct_answer': i % 4,
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

        # Verify count is 3
        template_details = client.get(f'/api/templates/{template_id}')
        assert template_details.status_code == 200
        details = json.loads(template_details.data)
        assert details['question_count'] == 3

        # Remove one question
        delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_ids[0]}')
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.data)
        assert delete_data['remaining_questions'] == 2

        # Verify count is now 2
        template_details = client.get(f'/api/templates/{template_id}')
        assert template_details.status_code == 200
        details = json.loads(template_details.data)
        assert details['question_count'] == 2

    def test_delete_from_empty_template(self, client):
        """Test removing a question from a template that has no questions."""
        # Create a template
        template_data = {
            'name': 'Empty Template',
            'description': 'Template with no questions',
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
            'content': 'Orphaned question?',
            'options': ['Yes', 'No', 'Maybe', 'Unknown'],
            'correct_answer': 0,
            'difficulty': 'easy'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Try to remove the question from the empty template
        response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
        assert response.status_code == 400
        error_data = json.loads(response.data)
        assert error_data['error'] == 'Question is not associated with this template'