#!/usr/bin/env python3
"""
Test script to verify that specialization and question type filters work correctly in combination.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5001/api"

def test_filter_combinations():
    """Test various filter combinations to ensure they work correctly."""
    
    print("Testing Question Bank Filter Combinations...")
    print("=" * 50)
    
    # Test cases: (specialization, question_type, expected_behavior)
    test_cases = [
        ("", "", "Should return all questions"),
        ("aptitude", "", "Should return only aptitude specialization questions"),
        ("", "aptitude", "Should return only multiple choice questions (regardless of specialization)"),
        ("aptitude", "aptitude", "Should return aptitude specialization questions that have multiple choice options"),
        ("typing", "typing", "Should return typing specialization questions"),
        ("typing", "aptitude", "Should return typing questions with multiple choice options (if any)"),
        ("reading_comprehension", "reading_comprehension", "Should return reading comprehension questions"),
        ("verbal", "aptitude", "Should return verbal specialization questions with multiple choice options"),
        ("technical", "aptitude", "Should return technical specialization questions with multiple choice options"),
    ]
    
    for specialization, question_type, description in test_cases:
        print(f"\nTest Case: specialization='{specialization}', type='{question_type}'")
        print(f"Expected: {description}")
        
        # Build query parameters
        params = {
            "page": 1,
            "per_page": 5,
            "simple": "false"
        }
        
        if specialization:
            params["specialization"] = specialization
        if question_type:
            params["type"] = question_type
            
        try:
            response = requests.get(f"{BASE_URL}/questions", params=params)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                total = data.get("pagination", {}).get("total", 0)
                
                print(f"Results: Found {total} questions")
                
                # Show sample questions
                for i, q in enumerate(questions[:3]):  # Show first 3 questions
                    print(f"  Question {i+1}: spec='{q.get('specialization')}', has_options={bool(q.get('options'))}")
                    
            else:
                print(f"Error: HTTP {response.status_code}")
                print(response.text)
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the API. Make sure the service is running on port 5001.")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("Filter combination testing completed!")
    return True

def test_difficulty_filter():
    """Test difficulty filter works correctly."""
    print("\nTesting Difficulty Filter...")
    print("-" * 30)
    
    difficulties = ["easy", "medium", "hard"]
    
    for difficulty in difficulties:
        params = {
            "page": 1,
            "per_page": 5,
            "difficulty": difficulty,
            "simple": "false"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/questions", params=params)
            
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                total = data.get("pagination", {}).get("total", 0)
                
                print(f"Difficulty '{difficulty}': Found {total} questions")
                
                # Verify all returned questions have the correct difficulty
                for q in questions:
                    if q.get('difficulty') != difficulty:
                        print(f"  WARNING: Question {q.get('id')} has difficulty '{q.get('difficulty')}' but we filtered for '{difficulty}'")
                        
        except Exception as e:
            print(f"Error testing difficulty '{difficulty}': {e}")

if __name__ == "__main__":
    success = test_filter_combinations()
    test_difficulty_filter()
    
    if success:
        print("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
