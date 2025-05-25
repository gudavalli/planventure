import requests
import json

try:
    # Get all questions to see what's available
    print("Fetching questions from assessment service...")
    response = requests.get('http://localhost:5001/api/questions')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        questions = response.json()
        print(f'Total questions available: {len(questions)}')
        
        # Group by specialization
        by_spec = {}
        for q in questions:
            spec = q.get('specialization', 'Unknown')
            if spec not in by_spec:
                by_spec[spec] = []
            by_spec[spec].append(q)
        
        print('\nQuestions by specialization:')
        for spec, qs in sorted(by_spec.items()):
            print(f'  {spec}: {len(qs)} questions')
            for q in qs[:2]:  # Show first 2 questions as examples
                content = q['content'][:60] + '...' if len(q['content']) > 60 else q['content']
                print(f'    - ID {q["id"]}: {content}')
            if len(qs) > 2:
                print(f'    ... and {len(qs) - 2} more')
            print()
    else:
        print(f'Failed to get questions: {response.text}')
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
