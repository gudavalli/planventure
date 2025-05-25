#!/usr/bin/env python3
import requests
import json

# Configuration
API_BASE = "http://localhost:5001/api"

def link_questions_to_template(template_id, question_ids, template_name):
    """Link questions to a template"""
    try:
        payload = {"question_ids": question_ids}
        response = requests.post(f"{API_BASE}/templates/{template_id}/questions", 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added {len(question_ids)} questions to '{template_name}' (ID: {template_id})")
            print(f"   Total questions in template: {result.get('question_count', 'N/A')}")
            return result
        else:
            print(f"❌ Failed to add questions to '{template_name}': {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error linking questions to '{template_name}': {e}")
        return None

def main():
    """Link questions to templates based on their roles"""
    
    print("🔗 Linking questions to assessment templates...\n")
    
    # Template ID mappings (from the earlier API response)
    templates = {
        2: "Frontend Developer Assessment",      # 60 min, 9 questions
        3: "Backend Developer Assessment",       # 75 min, 12 questions
        4: "Junior Developer Assessment",        # 45 min, 10 questions
        5: "Full Stack Developer Assessment",    # 90 min, 14 questions
        6: "Data Analyst Assessment",           # 60 min, 10 questions
        7: "Quick Skills Screening"            # 20 min, 5 questions
    }
    
    # Frontend Developer Assessment (Template ID: 2)
    frontend_questions = [
        1,   # JavaScript - difference between let and var
        2,   # React - useState hook
        3,   # CSS - font-weight bold
        25,  # HTML - hyperlink tag
        26,  # CSS - spacing between elements
        4,   # Aptitude - sequence
        16,  # Typing - quick brown fox
        33,  # Communication - active listening
        31,  # Soft skills - disagreeing with manager
    ]
    
    # Backend Developer Assessment (Template ID: 3)
    backend_questions = [
        19,  # Python - exception handling
        20,  # Python - range output
        21,  # Java - constants
        22,  # Java - collections with duplicates
        23,  # SQL - WHERE clause
        24,  # SQL - INNER JOIN
        27,  # Data structures - binary search tree
        28,  # Data structures - LIFO stack
        29,  # OS - deadlock
        30,  # Networking - HTTP
        5,   # Aptitude - logical reasoning
        32,  # Soft skills - task prioritization
    ]
    
    # Junior Developer Assessment (Template ID: 4)
    junior_questions = [
        1,   # JavaScript basics
        3,   # CSS basics
        25,  # HTML basics
        8,   # Aptitude - percentage
        9,   # Aptitude - train problem
        4,   # Aptitude - sequence
        16,  # Typing test
        33,  # Communication
        34,  # Teamwork
        31,  # Soft skills
    ]
    
    # Full Stack Developer Assessment (Template ID: 5)
    fullstack_questions = [
        1,   # JavaScript
        2,   # React
        19,  # Python
        20,  # Python range
        23,  # SQL WHERE
        24,  # SQL INNER JOIN
        25,  # HTML
        26,  # CSS
        27,  # Data structures
        28,  # LIFO principle
        18,  # Technical typing
        12,  # Reading comprehension
        31,  # Disagreement handling
        32,  # Task prioritization
    ]
    
    # Data Analyst Assessment (Template ID: 6)
    data_analyst_questions = [
        19,  # Python
        20,  # Python range
        23,  # SQL WHERE
        24,  # SQL INNER JOIN
        7,   # Aptitude - discount calculation
        8,   # Aptitude - percentage
        12,  # Reading comprehension - AI
        13,  # Reading comprehension - AI applications
        33,  # Communication
        32,  # Task prioritization
    ]
    
    # Quick Skills Screening (Template ID: 7)
    screening_questions = [
        4,   # Aptitude - sequence
        8,   # Aptitude - percentage
        16,  # Typing test
        33,  # Communication
        34,  # Teamwork
    ]
    
    # Link questions to templates
    question_mappings = {
        2: frontend_questions,
        3: backend_questions,
        4: junior_questions,
        5: fullstack_questions,
        6: data_analyst_questions,
        7: screening_questions
    }
    
    success_count = 0
    for template_id, question_ids in question_mappings.items():
        template_name = templates[template_id]
        result = link_questions_to_template(template_id, question_ids, template_name)
        if result:
            success_count += 1
        print()  # Empty line for readability
    
    print(f"📊 Summary: Successfully linked questions to {success_count}/{len(templates)} templates")
    
    # Verify by checking template question counts
    print("\n🔍 Verifying template question counts...")
    try:
        response = requests.get(f"{API_BASE}/templates")
        if response.status_code == 200:
            data = response.json()
            templates_list = data.get('templates', [])
            
            for template in templates_list:
                if template['id'] in templates:
                    print(f"   {template['name']}: {template['question_count']} questions")
        else:
            print(f"❌ Failed to verify templates: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying templates: {e}")

if __name__ == "__main__":
    main()
