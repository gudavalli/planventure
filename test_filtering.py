import requests
import json

# Test the API filtering
base_url = 'http://localhost:5001/api'

# Test filtering by aptitude type
print('=== Testing aptitude filter ===')
response = requests.get(f'{base_url}/questions?type=aptitude&simple=false')
if response.status_code == 200:
    data = response.json()
    print(f'Found {len(data["questions"])} aptitude questions')
    for q in data['questions'][:3]:  # Show first 3
        print(f'  - {q["specialization"]}: {q["content"][:50]}...')
else:
    print(f'Error: {response.status_code}')

print('\n=== Testing reading_comprehension filter ===')
response = requests.get(f'{base_url}/questions?type=reading_comprehension&simple=false')
if response.status_code == 200:
    data = response.json()
    print(f'Found {len(data["questions"])} reading comprehension questions')
    for q in data['questions'][:2]:  # Show first 2
        print(f'  - {q["specialization"]}: {q["content"][:50]}...')
else:
    print(f'Error: {response.status_code}')

print('\n=== Testing typing filter ===')
response = requests.get(f'{base_url}/questions?type=typing&simple=false')
if response.status_code == 200:
    data = response.json()
    print(f'Found {len(data["questions"])} typing questions')
    for q in data['questions'][:2]:  # Show first 2
        print(f'  - {q["specialization"]}: {q["content"][:50]}...')
else:
    print(f'Error: {response.status_code}')
