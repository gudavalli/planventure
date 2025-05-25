#!/usr/bin/env python3
import requests
import json

def examine_questions():
    """Examine available questions and categorize them for template assignment"""
    try:
        response = requests.get("http://localhost:5001/api/questions")
        response.raise_for_status()
        questions = response.json()  # Response is a list directly
        
        print(f"Total questions available: {len(questions)}")
        print("\nQuestions by specialization:")
        
        # Group questions by specialization
        categories = {}
        for q in questions:
            category = q.get('specialization', 'Unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'id': q['id'],
                'content': q['content'][:80] + '...' if len(q['content']) > 80 else q['content'],
                'options_count': len(q.get('options', [])) if q.get('options') else 0
            })
        
        for category, questions_list in categories.items():
            print(f"\n{category.upper()} ({len(questions_list)} questions):")
            for q in questions_list:
                print(f"  ID {q['id']}: {q['content']} (Options: {q['options_count']})")
        
        return categories
        
    except Exception as e:
        print(f"Error examining questions: {e}")
        return {}

if __name__ == "__main__":
    examine_questions()
