#!/usr/bin/env python3
import requests

response = requests.get('http://localhost:5001/api/templates')
data = response.json()

print("📊 Template Question Counts:")
for t in data['templates']:
    print(f"  {t['name']}: {t['question_count']} questions")
