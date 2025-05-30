#!/usr/bin/env python3
"""
Test script to verify the fix for question type vs specialization confusion.
This script tests the API endpoints to ensure they're correctly handling both fields.
"""
import requests
import json
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:5001/api"  # Updated to include /api path and correct port
TOKEN = None  # Will be set after login

def login():
    """Log in and get access token"""
    login_data = {
        "email": "admin@planventure.com",  # Updated to match the actual admin credentials
        "password": "admin123"              # Updated password
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        response.raise_for_status()
        global TOKEN
        TOKEN = response.json()["access_token"]
        logger.info("Login successful")
        return True
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return False

def get_auth_headers():
    """Get headers with auth token"""
    # No authentication needed for test backend
    return {
        "Content-Type": "application/json"
    }

def test_create_question():
    """Test creating a question with both question_type and specialization"""
    # Test data for different combinations of question types and specializations
    test_cases = [
        {
            "name": "Multiple Choice - Aptitude",
            "data": {
                "question_type": "multiple_choice",
                "specialization": "aptitude",
                "content": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "difficulty": "easy",
                "explanation": "Basic addition",
                "time_limit": 30
            }
        },
        {
            "name": "Multiple Choice - Quantitative",
            "data": {
                "question_type": "multiple_choice",
                "specialization": "quantitative",
                "content": "What is the square root of 16?",
                "options": ["2", "4", "8", "16"],
                "correct_answer": "4",
                "difficulty": "medium",
                "explanation": "Square root calculation",
                "time_limit": 60
            }
        },
        {
            "name": "Reading Comprehension - Verbal",
            "data": {
                "question_type": "reading_comprehension",
                "specialization": "verbal",
                "content": "According to the passage, what is the main idea?",
                "reading_set": {
                    "content": "This is a sample reading passage for testing purposes. It contains multiple sentences and ideas to test comprehension."
                },
                "options": ["Testing", "Reading", "Comprehension", "All of the above"],
                "correct_answer": "All of the above",
                "difficulty": "medium",
                "explanation": "The passage covers all aspects mentioned",
                "time_limit": 120
            }
        },
        {
            "name": "Typing Test - Typing",
            "data": {
                "question_type": "typing",
                "specialization": "typing",
                "content": "The quick brown fox jumps over the lazy dog. This is a typing test that contains more than fifty characters to meet the minimum requirement.",
                "difficulty": "medium",
                "time_limit": 60
            }
        }
    ]
    
    question_ids = []
    
    for test_case in test_cases:
        try:
            logger.info(f"Creating question: {test_case['name']}")
            response = requests.post(
                f"{API_URL}/questions",
                headers=get_auth_headers(),
                json=test_case['data']
            )
            response.raise_for_status()
            result = response.json()
            question_id = result.get("id")
            
            if question_id:
                question_ids.append(question_id)
                logger.info(f"Created question with ID: {question_id}")
            else:
                logger.warning("Question created but no ID returned")
            
            # Small delay to prevent rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Failed to create question {test_case['name']}: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
    
    return question_ids

def test_fetch_questions(question_ids):
    """Test fetching questions with filters for both question_type and specialization"""
    test_filters = [
        {"name": "No filters", "params": {}},
        {"name": "Multiple Choice type", "params": {"type": "multiple_choice"}},
        {"name": "Reading Comprehension type", "params": {"type": "reading_comprehension"}},
        {"name": "Typing type", "params": {"type": "typing"}},
        {"name": "Aptitude specialization", "params": {"specialization": "aptitude"}},
        {"name": "Quantitative specialization", "params": {"specialization": "quantitative"}},
        {"name": "Verbal specialization", "params": {"specialization": "verbal"}},
        {"name": "Multiple Choice + Quantitative", "params": {"type": "multiple_choice", "specialization": "quantitative"}}
    ]
    
    for test_filter in test_filters:        try:
            logger.info(f"Fetching questions with filter: {test_filter['name']}")
            response = requests.get(
                f"{API_URL}/questions",
                headers=get_auth_headers(),
                params=test_filter['params']
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle both formats: list or object with 'questions' field
            if isinstance(result, list):
                questions = result
            else:
                questions = result.get("questions", [])
            
            logger.info(f"Found {len(questions)} questions with filter: {test_filter['name']}")
            
            if questions:
                # Display the first question's details for verification
                first = questions[0]
                logger.info(f"Sample question - ID: {first.get('id')}, Type: {first.get('question_type')}, Specialization: {first.get('specialization')}")
            
            # Small delay to prevent rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Failed to fetch questions with filter {test_filter['name']}: {str(e)}")

def test_fetch_question_details(question_ids):
    """Test fetching individual question details"""
    for question_id in question_ids:
        try:
            logger.info(f"Fetching details for question ID: {question_id}")
            response = requests.get(
                f"{API_URL}/questions/{question_id}",
                headers=get_auth_headers()
            )
            response.raise_for_status()
            question = response.json()
            
            logger.info(f"Question details - ID: {question.get('id')}")
            logger.info(f"  Content: {question.get('content')[:50]}...")
            logger.info(f"  Question Type: {question.get('question_type')}")
            logger.info(f"  Specialization: {question.get('specialization')}")
            
            # Verify that both question_type and specialization fields exist
            if not question.get('question_type'):
                logger.error("question_type field is missing or empty")
            if not question.get('specialization'):
                logger.error("specialization field is missing or empty")
            
            # Small delay to prevent rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Failed to fetch question details for ID {question_id}: {str(e)}")

def test_update_question(question_ids):
    """Test updating questions with both question_type and specialization"""
    if not question_ids:
        logger.warning("No question IDs available for update test")
        return
    
    # Use the first question for the update test
    question_id = question_ids[0]
    
    try:
        # First fetch the current question
        response = requests.get(
            f"{API_URL}/questions/{question_id}",
            headers=get_auth_headers()
        )
        response.raise_for_status()
        question = response.json()
        
        # Modify both question_type and specialization
        update_data = {
            "question_type": "multiple_choice" if question.get("question_type") != "multiple_choice" else "reading_comprehension",
            "specialization": "logical" if question.get("specialization") != "logical" else "technical",
            "content": f"Updated question content at {time.time()}"
        }
        
        logger.info(f"Updating question ID: {question_id}")
        logger.info(f"  From Type: {question.get('question_type')} -> To Type: {update_data['question_type']}")
        logger.info(f"  From Specialization: {question.get('specialization')} -> To Specialization: {update_data['specialization']}")
        
        response = requests.put(
            f"{API_URL}/questions/{question_id}",
            headers=get_auth_headers(),
            json=update_data
        )
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"Question updated: {result.get('message', 'Success')}")
        
        # Verify the update
        response = requests.get(
            f"{API_URL}/questions/{question_id}",
            headers=get_auth_headers()
        )
        response.raise_for_status()
        updated = response.json()
        
        logger.info(f"Verified update - Question Type: {updated.get('question_type')}, Specialization: {updated.get('specialization')}")
        
        # Check if the update was applied correctly
        if updated.get("question_type") != update_data["question_type"]:
            logger.error(f"question_type was not updated correctly. Expected: {update_data['question_type']}, Got: {updated.get('question_type')}")
        if updated.get("specialization") != update_data["specialization"]:
            logger.error(f"specialization was not updated correctly. Expected: {update_data['specialization']}, Got: {updated.get('specialization')}")
        
    except Exception as e:
        logger.error(f"Failed to update question ID {question_id}: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")

def run_tests():
    """Run all tests for question_type vs specialization fix"""
    logger.info("Starting question_type vs specialization fix tests")
    
    # Skip login for test backend which doesn't require authentication
    # if not login():
    #     return
    
    question_ids = test_create_question()
    test_fetch_questions(question_ids)
    test_fetch_question_details(question_ids)
    test_update_question(question_ids)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    run_tests()
