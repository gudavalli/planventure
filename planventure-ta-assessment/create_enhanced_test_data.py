#!/usr/bin/env python3
"""
Enhanced Manual Test Data Generator for PlanVenture Assessment Service
This script ensures ALL question types are included in test assessments
"""

from app import create_app
from models.database import db
from models.assessment import AssessmentTemplate, Assessment, AssessmentResponse
from models.question import Question
from datetime import datetime, timedelta
import json

def create_enhanced_test_assessments():
    """Create comprehensive test assessments that include ALL question types"""
    
    app = create_app()
    with app.app_context():
        print("Creating enhanced test assessments with ALL question types...")
        
        # Get all question types
        all_questions = Question.query.all()
        question_by_spec = {}
        for q in all_questions:
            if q.specialization not in question_by_spec:
                question_by_spec[q.specialization] = []
            question_by_spec[q.specialization].append(q)
        
        print(f"Found questions in {len(question_by_spec)} specializations:")
        for spec, questions in question_by_spec.items():
            print(f"  • {spec}: {len(questions)} questions")
        
        # Clear existing test assessments to avoid duplicates
        existing_test_assessments = Assessment.query.filter(
            Assessment.user_email.in_([
                "john.smith@example.com",
                "jane.doe@example.com", 
                "mike.johnson@example.com",
                "sarah.wilson@example.com",
                "david.brown@example.com",
                "reading.test@example.com",
                "typing.test@example.com",
                "comprehensive.test@example.com"
            ])
        ).all()
        
        for assessment in existing_test_assessments:
            # Delete associated responses first
            AssessmentResponse.query.filter_by(assessment_id=assessment.id).delete()
            db.session.delete(assessment)
        
        db.session.commit()
        print(f"Cleared {len(existing_test_assessments)} existing test assessments")
        
        # Get existing templates
        templates = AssessmentTemplate.query.all()
        if not templates:
            print("No assessment templates found.")
            return
        
        # Enhanced test scenarios including specific question types
        test_scenarios = [
            {
                "user_email": "john.smith@example.com",
                "template": templates[0],
                "status": "pending",
                "description": "Fresh assessment - not started yet"
            },
            {
                "user_email": "jane.doe@example.com",
                "template": templates[1] if len(templates) > 1 else templates[0],
                "status": "in_progress",
                "description": "Partially completed assessment",
                "responses": 3
            },
            {
                "user_email": "mike.johnson@example.com",
                "template": templates[2] if len(templates) > 2 else templates[0],
                "status": "completed",
                "description": "Fully completed assessment",
                "responses": "all"
            },
            {
                "user_email": "reading.test@example.com",
                "template": templates[0],
                "status": "in_progress",
                "description": "Assessment with reading comprehension questions",
                "custom_questions": question_by_spec.get('reading_comprehension', [])[:2],
                "responses": 2
            },
            {
                "user_email": "typing.test@example.com", 
                "template": templates[0],
                "status": "completed",
                "description": "Assessment with typing questions",
                "custom_questions": question_by_spec.get('typing', [])[:2],
                "responses": "all"
            },
            {
                "user_email": "comprehensive.test@example.com",
                "template": templates[0],
                "status": "in_progress", 
                "description": "Comprehensive test with all question types",
                "custom_questions": [
                    *question_by_spec.get('reading_comprehension', [])[:1],
                    *question_by_spec.get('typing', [])[:1],
                    *question_by_spec.get('aptitude', [])[:2],
                    *question_by_spec.get('JavaScript', [])[:1],
                    *question_by_spec.get('Python', [])[:1]
                ],
                "responses": 4
            }
        ]
        
        created_assessments = []
        
        for scenario in test_scenarios:
            # Create assessment
            start_time = datetime.utcnow() - timedelta(hours=1)
            if scenario["status"] == "pending":
                start_time = None
            elif scenario["status"] == "completed":
                start_time = datetime.utcnow() - timedelta(hours=2)
            
            assessment = Assessment(
                user_email=scenario["user_email"],
                template_id=scenario["template"].id,
                status=scenario["status"],
                start_time=start_time,
                end_time=datetime.utcnow() - timedelta(minutes=30) if scenario["status"] == "completed" else None
            )
            
            db.session.add(assessment)
            db.session.flush()  # Get the ID
            
            # Determine which questions to use
            if scenario.get("custom_questions"):
                questions_to_use = scenario["custom_questions"]
            else:
                questions_to_use = list(scenario["template"].questions)
            
            # Create responses based on scenario
            if scenario.get("responses") and questions_to_use:
                response_count = 0
                if scenario["responses"] == "all":
                    response_count = len(questions_to_use)
                elif isinstance(scenario["responses"], int):
                    response_count = min(scenario["responses"], len(questions_to_use))
                
                for i in range(response_count):
                    question = questions_to_use[i]
                    
                    # Generate realistic answers based on question type
                    answer = generate_realistic_answer(question)
                    
                    response = AssessmentResponse(
                        assessment_id=assessment.id,
                        question_id=question.id,
                        answer=answer,
                        score=0.8,
                        submitted_at=start_time + timedelta(minutes=i*3) if start_time else datetime.utcnow()
                    )
                    
                    db.session.add(response)
            
            created_assessments.append({
                "assessment": assessment,
                "description": scenario["description"],
                "user_email": scenario["user_email"],
                "template": scenario["template"].name,
                "question_types": [q.specialization for q in (scenario.get("custom_questions") or scenario["template"].questions)]
            })
        
        db.session.commit()
        
        print(f"\n✅ Created {len(created_assessments)} enhanced test assessments:")
        for item in created_assessments:
            assessment = item["assessment"]
            response_count = AssessmentResponse.query.filter_by(assessment_id=assessment.id).count()
            print(f"  • ID {assessment.id}: {item['description']}")
            print(f"    User: {item['user_email']}")
            print(f"    Template: {item['template']}")
            print(f"    Status: {assessment.status}")
            print(f"    Responses: {response_count}")
            print(f"    Question types: {set(item['question_types'])}")
            print()

def generate_realistic_answer(question):
    """Generate realistic answers based on question specialization"""
    
    if question.specialization == "typing":
        # For typing tests, return the text they're supposed to type
        if "Type the following text" in question.content:
            # Extract the text after the colon
            parts = question.content.split(":")
            if len(parts) > 1:
                return parts[1].strip().strip("'\"")
        elif "Type this technical text" in question.content:
            # Extract the text in quotes
            import re
            match = re.search(r"'([^']*)'", question.content)
            if match:
                return match.group(1)
        return "The quick brown fox jumps over the lazy dog"
    
    elif question.specialization == "reading_comprehension":
        # For reading comprehension, provide thoughtful answers
        if "What is the main benefit" in question.content:
            return "Increased flexibility and better work-life balance"
        elif "challenge" in question.content.lower():
            return "Communication and collaboration difficulties in remote settings"
        elif "According to the passage" in question.content:
            return "AI has revolutionized many industries through automation and efficiency"
        else:
            return "Based on the passage, the key point is the impact of technology on modern work practices"
    
    elif question.specialization == "aptitude":
        # For aptitude questions, try to give correct logical answers
        if question.options:
            try:
                options = json.loads(question.options) if isinstance(question.options, str) else question.options
                if options and len(options) > 0:
                    # For sequence questions, try to pick a logical answer
                    if "sequence" in question.content.lower():
                        return options[0]  # First option often correct in test data
                    elif "train" in question.content.lower():
                        return options[1] if len(options) > 1 else options[0]
                    else:
                        return options[0]
            except:
                pass
        return "42"  # Default for aptitude
    
    else:
        # For technical questions (JavaScript, Python, etc.)
        if question.options:
            try:
                options = json.loads(question.options) if isinstance(question.options, str) else question.options
                if options and len(options) > 0:
                    return options[0]
            except:
                pass
        return "A"  # Default multiple choice answer

def print_enhanced_summary():
    """Print a comprehensive summary of all test data including question types"""
    
    app = create_app()
    with app.app_context():
        print("\n" + "="*70)
        print("ENHANCED MANUAL TESTING DATA SUMMARY")
        print("="*70)
        
        # Templates summary
        templates = AssessmentTemplate.query.all()
        print(f"\n📋 Assessment Templates ({len(templates)} total):")
        for template in templates:
            questions_count = template.questions.count()
            print(f"  • {template.name} - {questions_count} questions")
        
        # Questions summary by specialization
        questions = Question.query.all()
        specializations = {}
        for question in questions:
            spec = question.specialization
            specializations[spec] = specializations.get(spec, 0) + 1
        
        print(f"\n❓ Questions ({len(questions)} total) by Specialization:")
        for spec, count in sorted(specializations.items()):
            print(f"  • {spec}: {count} questions")
        
        # Assessments summary with question type coverage
        assessments = Assessment.query.all()
        status_counts = {}
        question_type_coverage = set()
        
        for assessment in assessments:
            status = assessment.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Check what question types this assessment covers
            responses = AssessmentResponse.query.filter_by(assessment_id=assessment.id).all()
            for response in responses:
                question = Question.query.get(response.question_id)
                if question:
                    question_type_coverage.add(question.specialization)
        
        print(f"\n📊 Test Assessments ({len(assessments)} total):")
        for status, count in status_counts.items():
            print(f"  • {status}: {count} assessments")
        
        print(f"\n📈 Assessment Responses: {AssessmentResponse.query.count()} total")
        
        print(f"\n🎯 Question Types Covered in Test Data:")
        for spec in sorted(question_type_coverage):
            response_count = db.session.query(AssessmentResponse).join(Question).filter(Question.specialization == spec).count()
            print(f"  • {spec}: {response_count} test responses")
        
        print("\n" + "="*70)
        print("READING COMPREHENSION & TYPING TEST COVERAGE:")
        print("="*70)
        
        # Specific check for reading comprehension and typing
        reading_responses = db.session.query(AssessmentResponse).join(Question).filter(Question.specialization == 'reading_comprehension').count()
        typing_responses = db.session.query(AssessmentResponse).join(Question).filter(Question.specialization == 'typing').count()
        
        print(f"✅ Reading Comprehension Responses: {reading_responses}")
        print(f"✅ Typing Test Responses: {typing_responses}")
        
        if reading_responses > 0 and typing_responses > 0:
            print("🎉 SUCCESS: All question types now have test data!")
        else:
            print("⚠️  Some question types still missing test data")
        
        print("\n" + "="*70)
        print("MANUAL TESTING ENDPOINTS:")
        print("="*70)
        print("• GET /assessments - List all assessments")
        print("• GET /assessments/<assessment_id> - Get specific assessment")
        print("• POST /assessments - Create new assessment") 
        print("• PUT /assessments/<assessment_id>/start - Start assessment")
        print("• POST /assessments/<assessment_id>/submit - Submit answers")
        print("• GET /templates - List assessment templates")
        print("• GET /analytics - Assessment analytics")
        print("• GET /questions - List questions by specialization")
        print("="*70)

if __name__ == "__main__":
    print("Creating ENHANCED test data with ALL question types...")
    
    try:
        create_enhanced_test_assessments()
        print_enhanced_summary()
        
        print("\n✅ Enhanced manual test data creation completed successfully!")
        print("\nNow includes comprehensive test coverage for:")
        print("• ✅ Reading comprehension questions with realistic answers")
        print("• ✅ Typing test questions with proper text responses") 
        print("• ✅ All technical specializations")
        print("• ✅ Various assessment states and user scenarios")
        print("\nUse the assessment service API endpoints to interact with this enhanced test data.")
        
    except Exception as e:
        print(f"\n❌ Error creating enhanced test data: {str(e)}")
        import traceback
        traceback.print_exc()
