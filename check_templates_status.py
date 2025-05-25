#!/usr/bin/env python3
import requests

def check_templates():
    try:
        response = requests.get("http://localhost:5001/api/templates")
        response.raise_for_status()
        templates = response.json()
        
        print("Current Template Status:")
        print("=" * 50)
        for template in templates:
            print(f"ID {template['id']}: {template['name']}")
            print(f"  Duration: {template['duration']} minutes")
            print(f"  Questions: {template['question_count']}")
            print(f"  Created: {template['created_at'][:10]}")
            print()
            
    except Exception as e:
        print(f"Error checking templates: {e}")

if __name__ == "__main__":
    check_templates()
