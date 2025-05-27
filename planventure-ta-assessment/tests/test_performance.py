"""
Performance tests for the assessment system DELETE endpoint
"""
import pytest
import json
import time
from tests.conftest import create_test_question, create_test_template


class TestDeleteEndpointPerformance:
    """Performance tests for DELETE endpoint"""
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_delete_question_performance(self, client, benchmark):
        """Test DELETE endpoint performance"""
        # Create test data once
        template_data = create_test_template(client)
        
        def delete_operation():
            # Create fresh question and add to template for each benchmark iteration
            question_data = create_test_question(client)
            client.post(f'/api/templates/{template_data["id"]}/questions/{question_data["id"]}')
            
            # Perform the delete operation
            response = client.delete(f'/api/templates/{template_data["id"]}/questions/{question_data["id"]}')
            return response
        
        # Benchmark the delete operation
        result = benchmark(delete_operation)
        assert result.status_code == 200
    
    @pytest.mark.performance
    def test_bulk_delete_performance(self, client):
        """Test performance with multiple delete operations"""
        template_data = create_test_template(client)
        question_ids = []
        
        # Create multiple questions
        for i in range(10):
            question_data = create_test_question(client)
            question_ids.append(question_data["id"])
            # Add to template
            client.post(f'/api/templates/{template_data["id"]}/questions/{question_data["id"]}')
        
        start_time = time.time()
        
        # Delete all questions
        for question_id in question_ids:
            response = client.delete(f'/api/templates/{template_data["id"]}/questions/{question_id}')
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Assert performance threshold (should complete within 2 seconds)
        assert duration < 2.0, f"Bulk delete took {duration:.2f} seconds, expected < 2.0"
    
    @pytest.mark.performance
    def test_concurrent_delete_simulation(self, client):
        """Simulate concurrent delete operations"""
        template_data = create_test_template(client)
        
        # Create multiple questions
        questions = []
        for i in range(5):
            question_data = create_test_question(client)
            questions.append(question_data)
            # Add to template
            client.post(f'/api/templates/{template_data["id"]}/questions/{question_data["id"]}')
        
        start_time = time.time()
        
        # Simulate rapid successive deletes
        for question in questions:
            response = client.delete(f'/api/templates/{template_data["id"]}/questions/{question["id"]}')
            # Should succeed or return 404 if already deleted
            assert response.status_code in [200, 404]
        
        duration = time.time() - start_time
        
        # Should handle rapid requests efficiently
        assert duration < 1.0, f"Concurrent deletes took {duration:.2f} seconds"


class TestGetTemplateDetailsPerformance:
    """Performance tests for GET template details endpoint"""
    
    @pytest.mark.performance
    @pytest.mark.benchmark
    def test_get_template_with_many_questions_performance(self, client, benchmark):
        """Test GET template performance with many associated questions"""
        template_data = create_test_template(client)
        
        # Add multiple questions to template
        for i in range(20):
            question_data = create_test_question(client)
            client.post(f'/api/templates/{template_data["id"]}/questions/{question_data["id"]}')
        
        def get_template_operation():
            response = client.get(f'/api/templates/{template_data["id"]}')
            return response
        
        # Benchmark the get operation
        result = benchmark(get_template_operation)
        assert result.status_code == 200
        
        data = json.loads(result.data)
        assert data['question_count'] == 20
