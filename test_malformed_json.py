#!/usr/bin/env python3
"""
Test script to verify malformed JSON handling in the API
"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:5001/api"

def test_malformed_json():
    """Test sending malformed JSON to the API"""
    headers = {
        "Content-Type": "application/json"
    }
    
    # Test malformed JSON for question creation
    malformed_json = '{"content": "Test", "invalid": json}'
    
    try:
        logger.info("Sending malformed JSON to /questions endpoint")
        response = requests.post(
            f"{API_URL}/questions",
            headers=headers,
            data=malformed_json
        )
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    test_malformed_json()
