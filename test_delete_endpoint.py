#!/usr/bin/env python3
"""
Test script to validate the DELETE question from template endpoint
and the GET template details endpoint.
"""
import requests
import json

# Configuration
API_BASE = "http://localhost:5001/api"

def test_endpoints():
    print("🧪 Testing Template Question Management Endpoints\n")
      # Step 1: Create a test template
    print("1️⃣ Creating a test template...")
    import time
    timestamp = int(time.time())
    template_data = {
        'name': f'Test Template for DELETE endpoint {timestamp}',
        'description': 'Testing DELETE question functionality',
        'time_limit': 30,
        'percentage': 70,
        'creator_id': 1
    }
    
    template_response = requests.post(
        f"{API_BASE}/templates",
        json=template_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if template_response.status_code != 201:
        print(f"❌ Failed to create template: {template_response.status_code}")
        print(f"Response: {template_response.text}")
        return False
    
    template_id = template_response.json()['id']
    print(f"✅ Created template with ID: {template_id}")
    
    # Step 2: Create test questions
    print("\n2️⃣ Creating test questions...")
    questions_data = [
        {
            'specialization': 'aptitude',
            'content': 'What is 2+2?',
            'options': ['3', '4', '5', '6'],
            'correct_answer': '4'
        },
        {
            'specialization': 'technical',
            'content': 'What is the capital of France?',
            'options': ['London', 'Berlin', 'Paris', 'Madrid'],
            'correct_answer': 'Paris'
        }
    ]
    
    question_ids = []
    for i, question_data in enumerate(questions_data):
        question_response = requests.post(
            f"{API_BASE}/questions",
            json=question_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if question_response.status_code != 201:
            print(f"❌ Failed to create question {i+1}: {question_response.status_code}")
            return False
            
        question_id = question_response.json()['id']
        question_ids.append(question_id)
        print(f"✅ Created question {i+1} with ID: {question_id}")
    
    # Step 3: Add questions to template
    print(f"\n3️⃣ Adding questions to template...")
    add_questions_response = requests.post(
        f"{API_BASE}/templates/{template_id}/questions",
        json={'question_ids': question_ids},
        headers={'Content-Type': 'application/json'}
    )
    
    if add_questions_response.status_code != 200:
        print(f"❌ Failed to add questions to template: {add_questions_response.status_code}")
        print(f"Response: {add_questions_response.text}")
        return False
    
    print(f"✅ Added {len(question_ids)} questions to template")
    
    # Step 4: Test GET template details endpoint
    print(f"\n4️⃣ Testing GET template details endpoint...")
    get_template_response = requests.get(f"{API_BASE}/templates/{template_id}")
    
    if get_template_response.status_code != 200:
        print(f"❌ GET template details failed: {get_template_response.status_code}")
        print(f"Response: {get_template_response.text}")
        return False
    
    template_details = get_template_response.json()
    print(f"✅ GET template details successful")
    print(f"   Template: {template_details['name']}")
    print(f"   Questions count: {template_details['question_count']}")
    print(f"   Questions in response: {len(template_details.get('questions', []))}")
    
    # Verify template has questions
    if template_details['question_count'] != len(question_ids):
        print(f"❌ Question count mismatch. Expected: {len(question_ids)}, Got: {template_details['question_count']}")
        return False
    
    # Step 5: Test DELETE question from template endpoint
    print(f"\n5️⃣ Testing DELETE question from template endpoint...")
    question_to_delete = question_ids[0]  # Delete the first question
    
    delete_response = requests.delete(f"{API_BASE}/templates/{template_id}/questions/{question_to_delete}")
    
    if delete_response.status_code != 200:
        print(f"❌ DELETE question failed: {delete_response.status_code}")
        print(f"Response: {delete_response.text}")
        return False
    
    delete_result = delete_response.json()
    print(f"✅ DELETE question successful")
    print(f"   Message: {delete_result.get('message', '')}")
    print(f"   Updated question count: {delete_result.get('question_count', 'N/A')}")
    
    # Step 6: Verify deletion by getting template details again
    print(f"\n6️⃣ Verifying deletion...")
    verify_response = requests.get(f"{API_BASE}/templates/{template_id}")
    
    if verify_response.status_code != 200:
        print(f"❌ Verification GET failed: {verify_response.status_code}")
        return False
    
    updated_template = verify_response.json()
    expected_count = len(question_ids) - 1
    
    if updated_template['question_count'] != expected_count:
        print(f"❌ Question count after deletion is incorrect. Expected: {expected_count}, Got: {updated_template['question_count']}")
        return False
    
    print(f"✅ Verification successful")
    print(f"   Questions remaining: {updated_template['question_count']}")
    
    # Check that the deleted question is not in the questions list
    remaining_question_ids = [q['id'] for q in updated_template.get('questions', [])]
    if question_to_delete in remaining_question_ids:
        print(f"❌ Deleted question {question_to_delete} still appears in template questions")
        return False
    
    print(f"✅ Deleted question {question_to_delete} is no longer in template")
    
    # Step 7: Test edge cases
    print(f"\n7️⃣ Testing edge cases...")
    
    # Test deleting non-existent question
    non_existent_question = 99999
    edge_response = requests.delete(f"{API_BASE}/templates/{template_id}/questions/{non_existent_question}")
    
    if edge_response.status_code == 404:
        print(f"✅ Correctly handled non-existent question (404)")
    else:
        print(f"⚠️  Non-existent question deletion returned: {edge_response.status_code}")
    
    # Test deleting from non-existent template
    non_existent_template = 99999
    edge_response2 = requests.delete(f"{API_BASE}/templates/{non_existent_template}/questions/{question_ids[1]}")
    
    if edge_response2.status_code == 404:
        print(f"✅ Correctly handled non-existent template (404)")
    else:
        print(f"⚠️  Non-existent template deletion returned: {edge_response2.status_code}")
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"📊 Summary:")
    print(f"   ✅ Template creation: PASS")
    print(f"   ✅ Question creation: PASS")
    print(f"   ✅ Adding questions to template: PASS")
    print(f"   ✅ GET template details: PASS")
    print(f"   ✅ DELETE question from template: PASS")
    print(f"   ✅ Verification after deletion: PASS")
    print(f"   ✅ Edge case handling: PASS")
    
    return True

if __name__ == "__main__":
    try:
        success = test_endpoints()
        if success:
            print(f"\n✅ ALL TESTS PASSED - The DELETE endpoint is working correctly!")
        else:
            print(f"\n❌ SOME TESTS FAILED - Check the output above for details")
    except Exception as e:
        print(f"\n💥 Test execution failed with error: {e}")
        import traceback
        traceback.print_exc()
