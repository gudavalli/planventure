#!/usr/bin/env python3
"""
Comprehensive Test Questions Generator for PlanVenture HR Assessment System
Creates test questions for all supported question types:
1. Aptitude (logical reasoning, numerical, verbal)
2. Reading Comprehension (with passages)
3. Typing Tests
4. Technical Questions (various specializations)
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:5001/api"
HEADERS = {'Content-Type': 'application/json'}

def create_question(question_data):
    """Create a single question via API"""
    try:
        response = requests.post(f"{BASE_URL}/questions", 
                               headers=HEADERS, 
                               json=question_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created question: {question_data['content'][:50]}... (ID: {result['id']})")
            return result
        else:
            print(f"❌ Failed to create question: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating question: {e}")
        return None

def create_reading_comprehension_set(paragraph, questions):
    """Create a reading comprehension set with associated questions"""
    # Note: This would require a separate API endpoint for reading sets
    # For now, we'll create the questions individually with reading_comprehension specialization
    print(f"📚 Creating reading comprehension set with {len(questions)} questions")
    
    created_questions = []
    for question in questions:
        question_data = {
            "specialization": "reading_comprehension",
            "content": f"Based on the following passage:\n\n{paragraph}\n\nQuestion: {question['content']}",
            "options": question['options'],
            "correct_answer": question['correct_answer']
        }
        result = create_question(question_data)
        if result:
            created_questions.append(result)
        time.sleep(0.1)  # Brief pause between requests
    
    return created_questions

# ============================================================================
# 1. APTITUDE QUESTIONS
# ============================================================================

aptitude_questions = [
    # Logical Reasoning
    {
        "specialization": "aptitude",
        "content": "What comes next in the sequence: 2, 6, 12, 20, 30, ?",
        "options": ["40", "42", "44", "46"],
        "correct_answer": "42"
    },
    {
        "specialization": "aptitude", 
        "content": "If all Bloops are Razzles and all Razzles are Lazzles, then all Bloops are definitely Lazzles. This statement is:",
        "options": ["True", "False", "Cannot be determined", "Sometimes true"],
        "correct_answer": "True"
    },
    {
        "specialization": "aptitude",
        "content": "A clock shows 3:15. What is the angle between the hour and minute hands?",
        "options": ["0 degrees", "7.5 degrees", "15 degrees", "22.5 degrees"],
        "correct_answer": "7.5 degrees"
    },
    
    # Numerical Reasoning
    {
        "specialization": "aptitude",
        "content": "If a product costs $80 after a 20% discount, what was the original price?",
        "options": ["$96", "$100", "$104", "$120"],
        "correct_answer": "$100"
    },
    {
        "specialization": "aptitude",
        "content": "What is 15% of 240?",
        "options": ["32", "36", "40", "44"],
        "correct_answer": "36"
    },
    {
        "specialization": "aptitude",
        "content": "If Train A travels 60 mph and Train B travels 80 mph, and they start 140 miles apart traveling toward each other, when will they meet?",
        "options": ["1 hour", "1.5 hours", "2 hours", "2.5 hours"],
        "correct_answer": "1 hour"
    },
    
    # Verbal Reasoning
    {
        "specialization": "aptitude",
        "content": "Choose the word that best completes the analogy: Book is to Library as Painting is to ___",
        "options": ["Museum", "Artist", "Canvas", "Frame"],
        "correct_answer": "Museum"
    },
    {
        "specialization": "aptitude",
        "content": "Which word does NOT belong with the others?",
        "options": ["Apple", "Orange", "Banana", "Potato"],
        "correct_answer": "Potato"
    }
]

# ============================================================================
# 2. READING COMPREHENSION
# ============================================================================

reading_passages = [
    {
        "paragraph": """
        Artificial Intelligence (AI) has revolutionized many industries, from healthcare to finance. 
        Machine learning algorithms can now process vast amounts of data and identify patterns that 
        humans might miss. However, AI systems are only as good as the data they are trained on. 
        Biased data can lead to biased AI decisions, which is why data quality and diversity are 
        crucial for developing fair and effective AI systems. Companies must also consider the 
        ethical implications of AI deployment, ensuring that these powerful tools are used 
        responsibly and transparently.
        """,
        "questions": [
            {
                "content": "According to the passage, what is a key factor in developing fair AI systems?",
                "options": [
                    "Processing speed",
                    "Data quality and diversity", 
                    "Algorithm complexity",
                    "Cost effectiveness"
                ],
                "correct_answer": "Data quality and diversity"
            },
            {
                "content": "What does the passage suggest about AI's capabilities compared to humans?",
                "options": [
                    "AI is always better than humans",
                    "AI can identify patterns humans might miss",
                    "AI cannot process large amounts of data",
                    "AI is only useful in healthcare"
                ],
                "correct_answer": "AI can identify patterns humans might miss"
            }
        ]
    },
    {
        "paragraph": """
        Remote work has become increasingly common, especially after the global pandemic. 
        While it offers flexibility and eliminates commuting time, it also presents unique 
        challenges. Communication can become more difficult, team collaboration may suffer, 
        and employees might feel isolated. Successful remote work requires clear communication 
        protocols, regular check-ins, and the right technology tools. Companies that adapt 
        well to remote work often see increased employee satisfaction and reduced overhead costs.
        """,
        "questions": [
            {
                "content": "What is mentioned as a benefit of remote work?",
                "options": [
                    "Better team collaboration",
                    "Eliminates commuting time",
                    "Improved face-to-face communication",
                    "Guaranteed salary increase"
                ],
                "correct_answer": "Eliminates commuting time"
            },
            {
                "content": "According to the passage, what do companies need for successful remote work?",
                "options": [
                    "Larger office spaces",
                    "More employees",
                    "Clear communication protocols and right technology",
                    "Higher salaries"
                ],
                "correct_answer": "Clear communication protocols and right technology"
            }
        ]
    }
]

# ============================================================================
# 3. TYPING TEST QUESTIONS
# ============================================================================

typing_questions = [
    {
        "specialization": "typing",
        "content": "Type the following text as quickly and accurately as possible: 'The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for typing practice.'",
        "options": None,
        "correct_answer": None
    },
    {
        "specialization": "typing",
        "content": "Type this business paragraph: 'In today's competitive market, companies must adapt quickly to changing customer demands. Effective communication, innovative solutions, and exceptional customer service are key factors that determine business success.'",
        "options": None,
        "correct_answer": None
    },
    {
        "specialization": "typing",
        "content": "Type this technical text: 'Database normalization is the process of structuring a relational database to reduce data redundancy and improve data integrity. It involves organizing data into tables and establishing relationships between them.'",
        "options": None,
        "correct_answer": None
    }
]

# ============================================================================
# 4. TECHNICAL QUESTIONS - EXPANDED
# ============================================================================

technical_questions = [
    # Python
    {
        "specialization": "Python",
        "content": "What is the output of: print(list(range(5)))?",
        "options": ["[1, 2, 3, 4, 5]", "[0, 1, 2, 3, 4]", "[0, 1, 2, 3, 4, 5]", "Error"],
        "correct_answer": "[0, 1, 2, 3, 4]"
    },
    {
        "specialization": "Python",
        "content": "Which of the following is used to handle exceptions in Python?",
        "options": ["try-catch", "try-except", "catch-throw", "handle-error"],
        "correct_answer": "try-except"
    },
    
    # Java
    {
        "specialization": "Java",
        "content": "What is the correct way to declare a constant in Java?",
        "options": ["const int x = 5;", "final int x = 5;", "static int x = 5;", "readonly int x = 5;"],
        "correct_answer": "final int x = 5;"
    },
    {
        "specialization": "Java",
        "content": "Which collection allows duplicate elements in Java?",
        "options": ["Set", "List", "Map", "Queue"],
        "correct_answer": "List"
    },
    
    # SQL
    {
        "specialization": "SQL",
        "content": "Which SQL clause is used to filter rows?",
        "options": ["SELECT", "FROM", "WHERE", "ORDER BY"],
        "correct_answer": "WHERE"
    },
    {
        "specialization": "SQL",
        "content": "What does the SQL INNER JOIN do?",
        "options": [
            "Returns all rows from both tables",
            "Returns rows that have matching values in both tables",
            "Returns rows from left table only",
            "Returns rows from right table only"
        ],
        "correct_answer": "Returns rows that have matching values in both tables"
    },
    
    # HTML/CSS
    {
        "specialization": "HTML",
        "content": "Which HTML tag is used to create a hyperlink?",
        "options": ["<link>", "<a>", "<href>", "<url>"],
        "correct_answer": "<a>"
    },
    {
        "specialization": "CSS",
        "content": "Which CSS property controls the spacing between elements?",
        "options": ["padding", "margin", "border", "spacing"],
        "correct_answer": "margin"
    },
    
    # Data Structures
    {
        "specialization": "Data Structures",
        "content": "What is the time complexity of searching in a balanced binary search tree?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
        "correct_answer": "O(log n)"
    },
    {
        "specialization": "Data Structures",
        "content": "Which data structure follows LIFO (Last In, First Out) principle?",
        "options": ["Queue", "Stack", "Array", "LinkedList"],
        "correct_answer": "Stack"
    },
    
    # Operating Systems
    {
        "specialization": "Operating Systems",
        "content": "What is a deadlock in operating systems?",
        "options": [
            "When a program stops responding",
            "When two or more processes wait indefinitely for each other",
            "When memory is full",
            "When CPU usage is 100%"
        ],
        "correct_answer": "When two or more processes wait indefinitely for each other"
    },
    
    # Networking
    {
        "specialization": "Networking",
        "content": "What does HTTP stand for?",
        "options": [
            "HyperText Transfer Protocol",
            "HyperText Transmission Protocol", 
            "HyperLink Transfer Protocol",
            "HyperMedia Transfer Protocol"
        ],
        "correct_answer": "HyperText Transfer Protocol"
    }
]

# ============================================================================
# 5. SOFT SKILLS & HR QUESTIONS
# ============================================================================

hr_questions = [
    {
        "specialization": "Soft Skills",
        "content": "What is the best approach when you disagree with your manager's decision?",
        "options": [
            "Ignore the decision and do what you think is right",
            "Discuss your concerns respectfully and provide alternative suggestions",
            "Complain to other team members",
            "Follow the decision without question"
        ],
        "correct_answer": "Discuss your concerns respectfully and provide alternative suggestions"
    },
    {
        "specialization": "Soft Skills",
        "content": "How do you prioritize tasks when everything seems urgent?",
        "options": [
            "Work on the easiest tasks first",
            "Work on the most recent requests first",
            "Assess impact and deadlines, then prioritize accordingly",
            "Ask someone else to decide"
        ],
        "correct_answer": "Assess impact and deadlines, then prioritize accordingly"
    },
    {
        "specialization": "Communication",
        "content": "What is active listening?",
        "options": [
            "Talking more than the other person",
            "Preparing your response while the other person speaks",
            "Fully concentrating on and understanding what the speaker is saying",
            "Taking notes during conversation"
        ],
        "correct_answer": "Fully concentrating on and understanding what the speaker is saying"
    },
    {
        "specialization": "Teamwork",
        "content": "What should you do when a team member is not contributing effectively?",
        "options": [
            "Ignore the issue and do their work yourself",
            "Report them to management immediately",
            "Address the issue directly and offer support",
            "Exclude them from team activities"
        ],
        "correct_answer": "Address the issue directly and offer support"
    }
]

def main():
    """Create all test questions"""
    print("🚀 Creating comprehensive test questions for PlanVenture HR Assessment System")
    print("=" * 80)
    
    all_questions = []
    
    # 1. Create Aptitude Questions
    print("\n📊 Creating Aptitude Questions...")
    for question in aptitude_questions:
        result = create_question(question)
        if result:
            all_questions.append(result)
        time.sleep(0.1)
    
    # 2. Create Reading Comprehension Questions
    print("\n📚 Creating Reading Comprehension Questions...")
    for passage in reading_passages:
        created = create_reading_comprehension_set(passage["paragraph"], passage["questions"])
        all_questions.extend(created)
        time.sleep(0.2)
    
    # 3. Create Typing Questions  
    print("\n⌨️ Creating Typing Test Questions...")
    for question in typing_questions:
        result = create_question(question)
        if result:
            all_questions.append(result)
        time.sleep(0.1)
    
    # 4. Create Technical Questions
    print("\n💻 Creating Technical Questions...")
    for question in technical_questions:
        result = create_question(question)
        if result:
            all_questions.append(result)
        time.sleep(0.1)
    
    # 5. Create HR/Soft Skills Questions
    print("\n👥 Creating HR & Soft Skills Questions...")
    for question in hr_questions:
        result = create_question(question)
        if result:
            all_questions.append(result)
        time.sleep(0.1)
    
    print("\n" + "=" * 80)
    print(f"✅ Successfully created {len(all_questions)} test questions!")
    
    # Summary by specialization
    specializations = {}
    for q in all_questions:
        spec = q.get('specialization', 'Unknown')
        specializations[spec] = specializations.get(spec, 0) + 1
    
    print("\n📈 Questions created by specialization:")
    for spec, count in sorted(specializations.items()):
        print(f"  • {spec}: {count} questions")
    
    print(f"\n🎯 Test questions are ready for assessment creation!")

if __name__ == "__main__":
    main()
