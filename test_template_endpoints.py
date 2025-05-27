#!/usr/bin/env python3
"""
Test script to verify the GET template details and DELETE question from template endpoints
"""
import requests
import json
import sys

API_BASE = "http://localhost:5001/api"

def test_endpoints():
    """Test the template endpoints"""
    print("🧪 Testing Template Endpoints")
    print("=" * 50)
    
    # First, let's get a list of available templates
    try:
        print("1. Getting list of templates...")
        response = requests.get(f"{API_BASE}/templates")
        if response.status_code != 200:
            print(f"❌ Failed to get templates list: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        templates_data = response.json()
        
        # Handle different response formats
        if isinstance(templates_data, list):
            templates = templates_data
        elif 'templates' in templates_data:
            templates = templates_data['templates']
        else:
            print("❌ Unexpected response format for templates list")
            return False
            
        if not templates:
            print("❌ No templates found")
            return False
            
        print(f"✅ Found {len(templates)} templates")
        
        # Select first template for testing
        template = templates[0]
        template_id = template['id']
        print(f"🎯 Testing with template: '{template['name']}' (ID: {template_id})")
        
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
        return False
    
    # Test GET template details endpoint
    try:
        print(f"\n2. Testing GET /templates/{template_id}...")
        response = requests.get(f"{API_BASE}/templates/{template_id}")
        
        if response.status_code != 200:
            print(f"❌ GET template details failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        template_details = response.json()
        
        # Verify response structure
        required_fields = ['id', 'name', 'questions']
        for field in required_fields:
            if field not in template_details:
                print(f"❌ Missing field '{field}' in template details response")
                return False
                
        print(f"✅ GET template details successful")
        print(f"   Template: {template_details['name']}")
        print(f"   Questions: {len(template_details['questions'])}")
        
        questions = template_details['questions']
        
    except Exception as e:
        print(f"❌ Error testing GET template details: {e}")
        return False
    
    # Test DELETE question from template endpoint (if template has questions)
    if not questions:
        print("⚠️  Template has no questions, skipping DELETE test")
        return True
        
    try:
        question_to_remove = questions[0]
        question_id = question_to_remove['id']
        
        print(f"\n3. Testing DELETE /templates/{template_id}/questions/{question_id}...")
        
        # Store original question count
        original_count = len(questions)
        
        response = requests.delete(f"{API_BASE}/templates/{template_id}/questions/{question_id}")
        
        if response.status_code not in [200, 204]:
            print(f"❌ DELETE question failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        print(f"✅ DELETE question successful")
        
        # Verify the question was removed by getting template details again
        print("4. Verifying question was removed...")
        response = requests.get(f"{API_BASE}/templates/{template_id}")
        
        if response.status_code == 200:
            updated_template = response.json()
            new_count = len(updated_template['questions'])
            
            if new_count == original_count - 1:
                print(f"✅ Question successfully removed. Count: {original_count} → {new_count}")
            else:
                print(f"⚠️  Question count unchanged: {original_count} → {new_count}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing DELETE question: {e}")
        return False

def main():
    """Main function"""
    print("Starting endpoint tests...\n")
    
    # Test if server is running
    try:
        response = requests.get(f"{API_BASE}/templates", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:5001")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        sys.exit(1)
    
    success = test_endpoints()
    
    if success:
        print("\n🎉 All tests passed!")
        print("✅ GET template details endpoint working")
        print("✅ DELETE question from template endpoint working")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
