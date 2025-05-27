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

        # Create a question with correct field names
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

        # Verify question was added
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

        # Verify question was removed
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
            'correct_answer': 0,
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

    def test_get_template_details_not_found(self, client):
        """Test retrieving details for a non-existent template."""
        non_existent_id = 99999
        response = client.get(f'/api/templates/{non_existent_id}')
        assert response.status_code == 404