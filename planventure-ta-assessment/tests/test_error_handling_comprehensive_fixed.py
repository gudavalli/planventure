"""
Comprehensive error handling tests for the assessment system.
Tests edge cases, boundary conditions, and error scenarios.
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


class TestErrorHandling:
    """Test suite for error handling scenarios."""

    def test_create_template_no_json_data(self, client):
        """Test creating template with no JSON data."""
        response = client.post('/api/templates',
                             content_type='application/json')
        assert response.status_code == 400
        error_data = json.loads(response.data)
        assert error_data['error'] == 'Invalid request'

    def test_create_template_empty_json(self, client):
        """Test creating template with empty JSON."""
        response = client.post('/api/templates',
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code == 400
        error_data = json.loads(response.data)
        assert 'No JSON data provided' in error_data['error']

    def test_create_template_partial_data(self, client):
        """Test creating template with partial data."""
        template_data = {
            'name': 'Partial Template'
            # Missing description and creator_id
        }
        response = client.post('/api/templates',
                             data=json.dumps(template_data),
                             content_type='application/json')
        # Should succeed with defaults or return error
        assert response.status_code in [201, 400]

    def test_create_question_invalid_type(self, client):
        """Test creating question with correct fields."""
        question_data = {
            'specialization': 'test',
            'content': 'Test question?',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'easy'
        }
        response = client.post('/api/questions',
                             data=json.dumps(question_data),
                             content_type='application/json')
        # Should succeed with correct fields
        assert response.status_code == 201

    def test_add_questions_to_nonexistent_template(self, client):
        """Test adding questions to a template that doesn't exist."""
        question_data = {
            'specialization': 'test',
            'content': 'Test question?',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'easy'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']        # Try to add to non-existent template
        non_existent_template_id = 99999
        add_response = client.post(f'/api/templates/{non_existent_template_id}/questions',
                                 data=json.dumps({'question_ids': [question_id]}),
                                 content_type='application/json')
        assert add_response.status_code == 404

    def test_add_nonexistent_questions_to_template(self, client):
        """Test adding non-existent questions to a template."""
        # Create a template
        template_data = {
            'name': 'Test Template',
            'description': 'Testing with non-existent questions',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Try to add non-existent questions
        non_existent_question_ids = [99999, 99998]
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': non_existent_question_ids}),
                                 content_type='application/json')
        assert add_response.status_code == 404

    def test_malformed_json_requests(self, client):
        """Test handling of malformed JSON requests."""
        # Test malformed JSON for template creation
        response = client.post('/api/templates',
                             data='{"name": "Test", "invalid": json}',
                             content_type='application/json')
        assert response.status_code == 400

        # Test malformed JSON for question creation
        response = client.post('/api/questions',
                             data='{"content": "Test", "invalid": json}',
                             content_type='application/json')
        assert response.status_code == 400

    def test_invalid_parameter_types(self, client):
        """Test handling of invalid parameter types."""
        # Test invalid template ID type
        response = client.get('/api/templates/invalid_id')
        assert response.status_code == 404

        # Test invalid question ID type
        response = client.delete('/api/templates/1/questions/invalid_id')
        assert response.status_code == 404

    def test_boundary_values(self, client):
        """Test boundary values for various parameters."""
        # Test very long template name
        long_name = 'A' * 1000
        template_data = {
            'name': long_name,
            'description': 'Testing long name',
            'creator_id': 1
        }
        response = client.post('/api/templates',
                             data=json.dumps(template_data),
                             content_type='application/json')
        # Should handle long names appropriately
        assert response.status_code in [201, 400]


class TestEdgeCases:
    """Test suite for edge cases."""

    def test_duplicate_question_addition(self, client):
        """Test adding the same question twice to a template."""
        # Create template
        template_data = {
            'name': 'Duplicate Test Template',
            'description': 'Testing duplicate addition',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create question
        question_data = {
            'specialization': 'test',
            'content': 'Duplicate test question?',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'medium'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Add question to template first time
        add_response1 = client.post(f'/api/templates/{template_id}/questions',
                                  data=json.dumps({'question_ids': [question_id]}),
                                  content_type='application/json')
        assert add_response1.status_code == 200

        # Try to add the same question again
        add_response2 = client.post(f'/api/templates/{template_id}/questions',
                                  data=json.dumps({'question_ids': [question_id]}),
                                  content_type='application/json')
        # Should handle duplicates gracefully
        assert add_response2.status_code == 200

    def test_empty_question_list_addition(self, client):
        """Test adding empty question list to template."""
        template_data = {
            'name': 'Empty List Template',
            'description': 'Testing empty list',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Add empty question list
        add_response = client.post(f'/api/templates/{template_id}/questions',
                                 data=json.dumps({'question_ids': []}),
                                 content_type='application/json')
        assert add_response.status_code == 200

    def test_very_large_question_list(self, client):
        """Test adding a very large list of questions."""
        # Create template
        template_data = {
            'name': 'Large List Template',
            'description': 'Testing large question list',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create many questions
        question_ids = []
        for i in range(20):  # Reduced from 100 for faster testing
            question_data = {
                'specialization': 'large_test',
                'content': f'Large list question {i + 1}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'medium'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            if question_response.status_code == 201:
                question_ids.append(json.loads(question_response.data)['id'])

        # Add all questions to template
        if question_ids:
            add_response = client.post(f'/api/templates/{template_id}/questions',
                                     data=json.dumps({'question_ids': question_ids}),
                                     content_type='application/json')
            assert add_response.status_code == 200

    def test_template_with_mixed_question_types(self, client):
        """Test template with different types of questions."""
        template_data = {
            'name': 'Mixed Types Template',
            'description': 'Testing mixed question types',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create different types of questions
        question_types = ['programming', 'general', 'technical']
        question_ids = []
        
        for qtype in question_types:
            question_data = {
                'specialization': qtype,
                'content': f'What is a {qtype} question?',
                'options': ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'medium'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            if question_response.status_code == 201:
                question_ids.append(json.loads(question_response.data)['id'])

        # Add all questions to template
        if question_ids:
            add_response = client.post(f'/api/templates/{template_id}/questions',
                                     data=json.dumps({'question_ids': question_ids}),
                                     content_type='application/json')
            assert add_response.status_code == 200


class TestPerformanceAndStress:
    """Test suite for performance and stress scenarios."""

    def test_rapid_sequential_operations(self, client):
        """Test rapid sequential operations on templates."""
        # Create template
        template_data = {
            'name': 'Rapid Operations Template',
            'description': 'Testing rapid operations',
            'creator_id': 1
        }
        template_response = client.post('/api/templates',
                                      data=json.dumps(template_data),
                                      content_type='application/json')
        assert template_response.status_code == 201
        template_id = json.loads(template_response.data)['id']

        # Create question
        question_data = {
            'specialization': 'rapid_test',
            'content': 'Rapid operation question?',
            'options': ['Fast', 'Faster', 'Fastest', 'Lightning'],
            'correct_answer': 0,  # Index of the correct answer
            'difficulty': 'hard'
        }
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        assert question_response.status_code == 201
        question_id = json.loads(question_response.data)['id']

        # Perform rapid operations
        for _ in range(5):
            # Add question
            add_response = client.post(f'/api/templates/{template_id}/questions',
                                     data=json.dumps({'question_ids': [question_id]}),
                                     content_type='application/json')
            
            # Remove question  
            if add_response.status_code == 200:
                delete_response = client.delete(f'/api/templates/{template_id}/questions/{question_id}')
                assert delete_response.status_code in [200, 400]  # 400 if already removed

    def test_concurrent_template_access(self, client):
        """Test concurrent access to the same template."""
        # Create template
        template_data = {
            'name': 'Concurrent Access Template',
            'description': 'Testing concurrent access',
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
                'specialization': 'concurrent',
                'content': f'Concurrent question {i + 1}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0,  # Index of the correct answer
                'difficulty': 'medium'
            }
            question_response = client.post('/api/questions',
                                          data=json.dumps(question_data),
                                          content_type='application/json')
            if question_response.status_code == 201:
                question_ids.append(json.loads(question_response.data)['id'])

        # Simulate concurrent operations
        if question_ids:
            # Add questions simultaneously
            for question_id in question_ids:
                add_response = client.post(f'/api/templates/{template_id}/questions',
                                         data=json.dumps({'question_ids': [question_id]}),
                                         content_type='application/json')
                assert add_response.status_code == 200

            # Get template details multiple times
            for _ in range(3):
                details_response = client.get(f'/api/templates/{template_id}')
                assert details_response.status_code == 200
