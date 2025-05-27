"""
Integration tests for the assessment system
"""
import pytest
import json
import time
from tests.conftest import create_test_question, create_test_template


class TestAssessmentSystemIntegration:
    """Integration tests for the complete assessment workflow"""
    
    @pytest.mark.integration
    def test_complete_template_lifecycle(self, client):
        """Test complete template creation, question addition, and deletion workflow"""
        # 1. Create a template
        template_data = create_test_template(client)
        assert template_data['id'] is not None
        template_id = template_data['id']
        
        # 2. Create multiple questions
        questions = []
        for i in range(3):
            question_data = create_test_question(client)
            questions.append(question_data)
            assert question_data['id'] is not None
        
        # 3. Add questions to template
        for question in questions:
            response = client.post(f'/api/templates/{template_id}/questions/{question["id"]}')
            assert response.status_code == 200
        
        # 4. Verify template has correct question count
        response = client.get(f'/api/templates/{template_id}')
        assert response.status_code == 200
        template_details = json.loads(response.data)
        assert template_details['question_count'] == 3
        
        # 5. Remove questions one by one and verify count updates
        for i, question in enumerate(questions):
            response = client.delete(f'/api/templates/{template_id}/questions/{question["id"]}')
            assert response.status_code == 200
            
            # Verify count decreases
            response = client.get(f'/api/templates/{template_id}')
            template_details = json.loads(response.data)
            expected_count = len(questions) - (i + 1)
            assert template_details['question_count'] == expected_count
    
    @pytest.mark.integration
    def test_multiple_templates_with_shared_questions(self, client):
        """Test that questions can be shared across multiple templates"""
        # Create templates
        template1 = create_test_template(client)
        template2 = create_test_template(client)
        
        # Create a question
        question = create_test_question(client)
        
        # Add question to both templates
        response1 = client.post(f'/api/templates/{template1["id"]}/questions/{question["id"]}')
        response2 = client.post(f'/api/templates/{template2["id"]}/questions/{question["id"]}')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Remove from first template
        response = client.delete(f'/api/templates/{template1["id"]}/questions/{question["id"]}')
        assert response.status_code == 200
        
        # Question should still exist in second template
        response = client.get(f'/api/templates/{template2["id"]}')
        template2_details = json.loads(response.data)
        assert template2_details['question_count'] == 1
        
        # Question should still be accessible via API
        response = client.get(f'/api/questions/{question["id"]}')
        assert response.status_code == 200


class TestApiEndpointIntegration:
    """Integration tests for API endpoint interactions"""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_crud_operations_sequence(self, client):
        """Test Create, Read, Update, Delete sequence"""
        # Create template
        template_data = {
            'name': 'Integration Test Template',
            'description': 'Test Description',
            'percentage': 100.0,
            'time_limit': 60,
            'creator_id': 1
        }
        response = client.post('/api/templates',
                             data=json.dumps(template_data),
                             content_type='application/json')
        assert response.status_code == 201
        template = json.loads(response.data)
        
        # Read template
        response = client.get(f'/api/templates/{template["id"]}')
        assert response.status_code == 200
        retrieved_template = json.loads(response.data)
        assert retrieved_template['name'] == template_data['name']
        
        # Create and associate question
        question = create_test_question(client)
        response = client.post(f'/api/templates/{template["id"]}/questions/{question["id"]}')
        assert response.status_code == 200
        
        # Verify association
        response = client.get(f'/api/templates/{template["id"]}')
        template_details = json.loads(response.data)
        assert template_details['question_count'] == 1
        
        # Delete association
        response = client.delete(f'/api/templates/{template["id"]}/questions/{question["id"]}')
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f'/api/templates/{template["id"]}')
        template_details = json.loads(response.data)
        assert template_details['question_count'] == 0
