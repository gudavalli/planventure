#!/usr/bin/env python3
"""
Additional edge case tests for the DELETE endpoint
"""
import requests
import json
import random

BASE_URL = "http://127.0.0.1:5001/api"

def test_delete_same_question_twice():
    """Test trying to delete the same question twice"""
    print("🧪 Testing DELETE edge cases")
    
    # Create template
    template_data = {
        'name': f'Edge Case Template {random.randint(1, 1000000)}',
        'description': 'Template for edge case testing',
        'creator_id': 1
    }
    
    response = requests.post(f"{BASE_URL}/templates", json=template_data)
    template_id = response.json()['id']
    print(f"✅ Created template with ID: {template_id}")
    
    # Create question
    question_data = {
        'content': 'Edge case test question?',
        'specialization': 'aptitude',
        'options': ['A', 'B', 'C', 'D'],
        'correct_answer': 'A'
    }
    
    response = requests.post(f"{BASE_URL}/questions", json=question_data)
    question_id = response.json()['id']
    print(f"✅ Created question with ID: {question_id}")
    
    # Add question to template
    add_data = {'question_ids': [question_id]}
    response = requests.post(f"{BASE_URL}/templates/{template_id}/questions", json=add_data)
    print(f"✅ Added question to template")
    
    # Delete question once
    response = requests.delete(f"{BASE_URL}/templates/{template_id}/questions/{question_id}")
    if response.status_code == 200:
        print(f"✅ First DELETE successful")
    else:
        print(f"❌ First DELETE failed: {response.status_code}")
        return False
    
    # Try to delete the same question again
    response = requests.delete(f"{BASE_URL}/templates/{template_id}/questions/{question_id}")
    if response.status_code == 400:
        print(f"✅ Second DELETE correctly returned 400 (question not associated)")
        return True
    else:
        print(f"❌ Second DELETE should have returned 400, got: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_delete_question_from_empty_template():
    """Test deleting a question from a template with no questions"""
    # Create empty template
    template_data = {
        'name': f'Empty Template {random.randint(1, 1000000)}',
        'description': 'Empty template for testing',
        'creator_id': 1
    }
    
    response = requests.post(f"{BASE_URL}/templates", json=template_data)
    template_id = response.json()['id']
    
    # Create question but don't add it to template
    question_data = {
        'content': 'Unassociated question?',
        'specialization': 'aptitude',
        'options': ['A', 'B', 'C', 'D'],
        'correct_answer': 'A'
    }
    
    response = requests.post(f"{BASE_URL}/questions", json=question_data)
    question_id = response.json()['id']
    
    # Try to delete question from empty template
    response = requests.delete(f"{BASE_URL}/templates/{template_id}/questions/{question_id}")
    if response.status_code == 400:
        print(f"✅ DELETE from empty template correctly returned 400")
        return True
    else:
        print(f"❌ DELETE from empty template should have returned 400, got: {response.status_code}")
        return False

if __name__ == "__main__":
    test1_passed = test_delete_same_question_twice()
    test2_passed = test_delete_question_from_empty_template()
    
    if test1_passed and test2_passed:
        print("🎉 All edge case tests passed!")
    else:
        print("❌ Some edge case tests failed")
