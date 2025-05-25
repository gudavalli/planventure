import requests
import json

# Configuration
API_BASE = "http://localhost:5001/api"

def create_template(name, description, question_ids, total_time=None):
    """Create an assessment template"""
    template_data = {
        "name": name,
        "description": description,
        "question_ids": question_ids,
        "creator_id": 6  # Nancy Hayes - admin user
    }
    
    if total_time:
        template_data["total_time"] = total_time
    
    response = requests.post(f"{API_BASE}/templates", json=template_data)
    if response.status_code == 201:
        template = response.json()
        print(f"✅ Created template '{name}' (ID: {template['id']}) with {len(question_ids)} questions")
        return template
    else:
        print(f"❌ Failed to create template '{name}': {response.status_code} - {response.text}")
        return None

def main():
    print("Creating sample assessment templates...\n")
    
    # Frontend Developer Assessment
    frontend_questions = [
        1,   # JavaScript let vs var
        2,   # React state hook
        3,   # CSS bold text
        25,  # HTML hyperlink
        26,  # CSS spacing
        16,  # Basic typing test
        33,  # Active listening (communication)
        11,  # Aptitude - word association
        13,  # Aptitude - logical reasoning
    ]
    
    create_template(
        name="Frontend Developer Assessment",
        description="Comprehensive assessment for frontend developer candidates covering JavaScript, React, HTML/CSS, typing skills, and soft skills",
        question_ids=frontend_questions,
        total_time=60  # 60 minutes
    )
    
    # Backend Developer Assessment
    backend_questions = [
        19,  # Python output
        20,  # Python exceptions
        21,  # Java constants
        22,  # Java collections
        23,  # SQL WHERE clause
        24,  # SQL INNER JOIN
        27,  # Data structures - binary tree
        28,  # Data structures - stack (LIFO)
        29,  # Operating systems - deadlock
        30,  # Networking - HTTP
        17,  # Business typing test
        32,  # Task prioritization
    ]
    
    create_template(
        name="Backend Developer Assessment",
        description="Technical assessment for backend developers covering Python, Java, SQL, data structures, system concepts, and problem-solving skills",
        question_ids=backend_questions,
        total_time=75  # 75 minutes
    )
    
    # Junior Developer Assessment (Entry Level)
    junior_questions = [
        1,   # JavaScript basics
        25,  # HTML hyperlink
        3,   # CSS bold text
        19,  # Python basics
        23,  # SQL WHERE
        16,  # Basic typing
        11,  # Aptitude - word association
        10,  # Aptitude - analogy
        33,  # Communication
        34,  # Teamwork
    ]
    
    create_template(
        name="Junior Developer Assessment",
        description="Entry-level assessment covering basic programming concepts, web technologies, and essential soft skills",
        question_ids=junior_questions,
        total_time=45  # 45 minutes
    )
    
    # Full Stack Developer Assessment
    fullstack_questions = [
        1,   # JavaScript
        2,   # React
        19,  # Python
        23,  # SQL WHERE
        24,  # SQL INNER JOIN
        25,  # HTML
        26,  # CSS spacing
        27,  # Data structures
        28,  # Data structures
        18,  # Technical typing
        12,  # Aptitude - numerical
        15,  # Reading comprehension
        31,  # Soft skills - disagreement
        32,  # Task prioritization
    ]
    
    create_template(
        name="Full Stack Developer Assessment",
        description="Comprehensive assessment for full stack developers covering frontend, backend, databases, and professional skills",
        question_ids=fullstack_questions,
        total_time=90  # 90 minutes
    )
    
    # Data Analyst Assessment
    analyst_questions = [
        19,  # Python
        23,  # SQL WHERE
        24,  # SQL INNER JOIN
        12,  # Numerical reasoning
        9,   # Numerical aptitude
        14,  # Reading comprehension - remote work
        15,  # Reading comprehension - AI
        17,  # Business typing
        32,  # Task prioritization
        33,  # Communication
    ]
    
    create_template(
        name="Data Analyst Assessment",
        description="Assessment for data analyst positions focusing on Python, SQL, analytical thinking, and communication skills",
        question_ids=analyst_questions,
        total_time=60  # 60 minutes
    )
    
    # Quick Skills Screening (All Roles)
    screening_questions = [
        11,  # Aptitude - word association
        16,  # Basic typing
        33,  # Communication
        34,  # Teamwork
        32,  # Task prioritization
    ]
    
    create_template(
        name="Quick Skills Screening",
        description="Short screening assessment for initial candidate evaluation covering basic aptitude, typing, and soft skills",
        question_ids=screening_questions,
        total_time=20  # 20 minutes
    )
    
    print("\n🎉 Sample assessment templates created successfully!")
    print("\nTemplates created:")
    print("1. Frontend Developer Assessment (60 min, 9 questions)")
    print("2. Backend Developer Assessment (75 min, 12 questions)")
    print("3. Junior Developer Assessment (45 min, 10 questions)")
    print("4. Full Stack Developer Assessment (90 min, 14 questions)")
    print("5. Data Analyst Assessment (60 min, 10 questions)")
    print("6. Quick Skills Screening (20 min, 5 questions)")

if __name__ == "__main__":
    main()
