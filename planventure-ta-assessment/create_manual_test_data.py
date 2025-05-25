#!/usr/bin/env python3
"""
Manual Test Data Generator for PlanVenture Assessment Service
"""

from app import create_app
from models.database import db
from models.assessment import AssessmentTemplate, Assessment, AssessmentResponse
from models.question import Question
from datetime import datetime, timedelta
import json

def create_sample_assessments():
    """Create sample assessments for manual testing"""
    
    app = create_app()
    with app.app_context():
        print("Creating sample assessments for manual testing...")
        
        # Get existing templates
        templates = AssessmentTemplate.query.all()
        if not templates:
            print("No assessment templates found.")
            return
        
        print(f"Found {len(templates)} templates")
        for template in templates:
            questions_count = template.questions.count()
            print(f"  • {template.name} - {questions_count} questions")
        
        # Sample user emails
        test_users = [
            "john.smith@example.com",
            "jane.doe@example.com",
            "mike.johnson@example.com",
            "sarah.wilson@example.com",
            "david.brown@example.com",
        ]
        
        # Create assessments in different states
        assessment_scenarios = [
            {
                "user_email": test_users[0],
                "template": templates[0],
                "status": "pending",
                "description": "Fresh assessment - not started yet"
            },
            {
                "user_email": test_users[1],
                "template": templates[1] if len(templates) > 1 else templates[0],
                "status": "in_progress", 
                "description": "Partially completed assessment",
                "responses": 3
            },
            {
                "user_email": test_users[2],
                "template": templates[2] if len(templates) > 2 else templates[0],
                "status": "completed",
                "description": "Fully completed assessment",
                "responses": "all"
            },
            {
                "user_email": test_users[3],
                "template": templates[0],
                "status": "completed",
                "description": "Recently completed assessment",
                "responses": "all",
                "completed_hours_ago": 2
            },
            {
                "user_email": test_users[4], 
                "template": templates[1] if len(templates) > 1 else templates[0],
                "status": "in_progress",
                "description": "Assessment started but abandoned",
                "responses": 1,
                "started_days_ago": 3
            },
        ]
        
        created_assessments = []
        
        for scenario in assessment_scenarios:
            # Create assessment
            start_time = datetime.utcnow()
            if scenario.get("started_days_ago"):
                start_time = datetime.utcnow() - timedelta(days=scenario["started_days_ago"])
            elif scenario.get("completed_hours_ago"):
                start_time = datetime.utcnow() - timedelta(hours=scenario["completed_hours_ago"] + 1)
            
            assessment = Assessment(
                user_email=scenario["user_email"],
                template_id=scenario["template"].id,
                status=scenario["status"],
                start_time=start_time if scenario["status"] != "pending" else None,
                end_time=datetime.utcnow() - timedelta(hours=scenario.get("completed_hours_ago", 0)) 
                         if scenario["status"] == "completed" else None
            )
            
            db.session.add(assessment)
            db.session.flush()  # Get the ID
            
            # Create responses based on scenario
            if scenario.get("responses"):
                questions = list(scenario["template"].questions)
                if questions:
                    response_count = 0
                    if scenario["responses"] == "all":
                        response_count = len(questions)
                    elif isinstance(scenario["responses"], int):
                        response_count = min(scenario["responses"], len(questions))
                    
                    for i in range(response_count):
                        question = questions[i]
                        
                        # Generate sample answers
                        if question.specialization == "typing_test":
                            answer = "The quick brown fox jumps over the lazy dog"
                        elif question.specialization == "reading_comprehension":
                            answer = "This is a sample reading comprehension answer"
                        elif question.options:
                            try:
                                options = json.loads(question.options)
                                answer = options[0] if options else "A"
                            except:
                                answer = "A"
                        else:
                            answer = "Sample answer"
                        
                        response = AssessmentResponse(
                            assessment_id=assessment.id,
                            question_id=question.id,
                            answer=answer,
                            score=0.8,
                            submitted_at=start_time + timedelta(minutes=i*2) if start_time else datetime.utcnow()
                        )
                        
                        db.session.add(response)
            
            created_assessments.append({
                "assessment": assessment,
                "description": scenario["description"],
                "user_email": scenario["user_email"],
                "template": scenario["template"].name
            })
        
        db.session.commit()
        
        print(f"\n✅ Created {len(created_assessments)} sample assessments:")
        for item in created_assessments:
            assessment = item["assessment"]
            print(f"  • ID {assessment.id}: {item['description']}")
            print(f"    User: {item['user_email']}, Template: {item['template']}")
            print(f"    Status: {assessment.status}")
            print()

def print_test_data_summary():
    """Print a summary of all test data"""
    
    app = create_app()
    with app.app_context():
        print("\n" + "="*60)
        print("MANUAL TESTING DATA SUMMARY")
        print("="*60)
        
        # Templates summary
        templates = AssessmentTemplate.query.all()
        print(f"\n📋 Assessment Templates ({len(templates)} total):")
        for template in templates:
            questions_count = template.questions.count()
            print(f"  • {template.name} - {questions_count} questions")
        
        # Questions summary
        questions = Question.query.all()
        specializations = {}
        for question in questions:
            spec = question.specialization
            specializations[spec] = specializations.get(spec, 0) + 1
        
        print(f"\n❓ Questions ({len(questions)} total):")
        for spec, count in specializations.items():
            print(f"  • {spec}: {count} questions")
        
        # Assessments summary
        assessments = Assessment.query.all()
        status_counts = {}
        for assessment in assessments:
            status = assessment.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📊 Sample Assessments ({len(assessments)} total):")
        for status, count in status_counts.items():
            print(f"  • {status}: {count} assessments")
        
        print(f"\n📈 Assessment Responses: {AssessmentResponse.query.count()} total")
        
        print("\n" + "="*60)
        print("MANUAL TESTING ENDPOINTS TO TRY:")
        print("="*60)
        print("• GET /assessments - List all assessments")
        print("• GET /assessments/<assessment_id> - Get specific assessment")
        print("• POST /assessments - Create new assessment") 
        print("• PUT /assessments/<assessment_id>/start - Start assessment")
        print("• POST /assessments/<assessment_id>/submit - Submit answers")
        print("• GET /templates - List assessment templates")
        print("• GET /analytics - Assessment analytics")
        print("• GET /questions - List questions")
        print("="*60)

if __name__ == "__main__":
    print("Creating comprehensive test data for manual testing...")
    
    try:
        create_sample_assessments()
        print_test_data_summary()
        
        print("\n✅ Manual test data creation completed successfully!")
        print("\nYou can now test the assessment service with realistic data including:")
        print("• Assessments in different states (pending, in progress, completed)")
        print("• Various user scenarios and test cases")
        print("• Sample responses and timing data")
        print("\nUse the assessment service API endpoints to interact with this test data.")
        
    except Exception as e:
        print(f"\n❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()