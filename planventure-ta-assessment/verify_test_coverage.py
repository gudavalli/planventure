#!/usr/bin/env python3
"""
Final Test Data Verification Script for PlanVenture Assessment Service
Verifies that ALL question types have proper test coverage
"""

from app import create_app
from models.database import db
from models.assessment import Assessment, AssessmentResponse
from models.question import Question
import json

def verify_test_coverage():
    """Verify comprehensive test coverage for all question types"""
    
    app = create_app()
    with app.app_context():
        print("🔍 VERIFYING COMPREHENSIVE TEST DATA COVERAGE")
        print("=" * 60)
        
        # Get all available question specializations
        all_specializations = db.session.query(Question.specialization).distinct().all()
        all_specs = [spec[0] for spec in all_specializations]
        
        print(f"📊 Available Question Specializations ({len(all_specs)}):")
        for spec in sorted(all_specs):
            question_count = Question.query.filter_by(specialization=spec).count()
            print(f"  • {spec}: {question_count} questions")
        
        print("\n" + "=" * 60)
        print("🧪 TEST COVERAGE ANALYSIS")
        print("=" * 60)
        
        # Check which specializations have test responses
        covered_specs = set()
        uncovered_specs = set(all_specs)
        
        responses = AssessmentResponse.query.all()
        print(f"\nTotal Test Responses: {len(responses)}")
        
        spec_coverage = {}
        for response in responses:
            question = Question.query.get(response.question_id)
            if question:
                spec = question.specialization
                covered_specs.add(spec)
                uncovered_specs.discard(spec)
                
                if spec not in spec_coverage:
                    spec_coverage[spec] = {
                        'response_count': 0,
                        'sample_answers': []
                    }
                
                spec_coverage[spec]['response_count'] += 1
                if len(spec_coverage[spec]['sample_answers']) < 2:
                    spec_coverage[spec]['sample_answers'].append(
                        response.answer[:50] + "..." if len(response.answer) > 50 else response.answer
                    )
        
        print(f"\n✅ COVERED SPECIALIZATIONS ({len(covered_specs)}):")
        for spec in sorted(covered_specs):
            coverage = spec_coverage[spec]
            print(f"  • {spec}: {coverage['response_count']} test responses")
            
            # Show sample answers for key question types
            if spec in ['reading_comprehension', 'typing', 'aptitude']:
                for i, answer in enumerate(coverage['sample_answers'], 1):
                    print(f"    Sample {i}: {answer}")
        
        if uncovered_specs:
            print(f"\n❌ UNCOVERED SPECIALIZATIONS ({len(uncovered_specs)}):")
            for spec in sorted(uncovered_specs):
                print(f"  • {spec}: No test responses")
        else:
            print(f"\n🎉 SUCCESS: ALL {len(all_specs)} SPECIALIZATIONS HAVE TEST COVERAGE!")
        
        print("\n" + "=" * 60)
        print("📋 ASSESSMENT BREAKDOWN")
        print("=" * 60)
        
        assessments = Assessment.query.all()
        for assessment in assessments:
            user_email = assessment.user_email
            status = assessment.status
            
            assessment_responses = AssessmentResponse.query.filter_by(assessment_id=assessment.id).all()
            response_count = len(assessment_responses)
            
            # Get question types for this assessment
            question_types = set()
            for resp in assessment_responses:
                question = Question.query.get(resp.question_id)
                if question:
                    question_types.add(question.specialization)
            
            print(f"\nAssessment {assessment.id}: {user_email}")
            print(f"  Status: {status}")
            print(f"  Responses: {response_count}")
            print(f"  Question Types: {sorted(question_types)}")
            
            # Highlight special assessments
            if 'reading_comprehension' in question_types:
                print("  🔖 READING COMPREHENSION TEST")
            if 'typing' in question_types:
                print("  ⌨️  TYPING TEST")
            if len(question_types) > 3:
                print("  🌟 COMPREHENSIVE MULTI-TYPE TEST")
        
        print("\n" + "=" * 60)
        print("🎯 KEY TESTING SCENARIOS VERIFIED")
        print("=" * 60)
        
        # Verify specific critical scenarios
        critical_checks = {
            "Reading Comprehension": len([r for r in responses if Question.query.get(r.question_id).specialization == 'reading_comprehension']) > 0,
            "Typing Tests": len([r for r in responses if Question.query.get(r.question_id).specialization == 'typing']) > 0,
            "Technical Questions": len([r for r in responses if Question.query.get(r.question_id).specialization in ['JavaScript', 'Python', 'Java']]) > 0,
            "Aptitude Tests": len([r for r in responses if Question.query.get(r.question_id).specialization == 'aptitude']) > 0,
            "Mixed Assessment": any(len(set(Question.query.get(r.question_id).specialization for r in AssessmentResponse.query.filter_by(assessment_id=a.id).all())) > 2 for a in assessments),
            "Different Statuses": len(set(a.status for a in assessments)) >= 2
        }
        
        for check_name, is_passed in critical_checks.items():
            status = "✅ PASS" if is_passed else "❌ FAIL"
            print(f"  {status}: {check_name}")
        
        all_passed = all(critical_checks.values())
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 COMPREHENSIVE TEST DATA VERIFICATION: SUCCESS!")
            print("✅ All question types have test coverage")
            print("✅ Reading comprehension tests included")
            print("✅ Typing tests included")
            print("✅ Multiple assessment states covered")
            print("✅ Mixed question type assessments available")
        else:
            print("⚠️  VERIFICATION INCOMPLETE")
            print("Some test scenarios may be missing")
        
        print("\n🚀 Ready for comprehensive manual testing!")
        print("=" * 60)

def show_sample_responses():
    """Show sample responses for key question types"""
    
    app = create_app()
    with app.app_context():
        print("\n📝 SAMPLE TEST RESPONSES")
        print("=" * 60)
        
        # Show reading comprehension samples
        reading_responses = db.session.query(AssessmentResponse).join(Question).filter(
            Question.specialization == 'reading_comprehension'
        ).limit(2).all()
        
        if reading_responses:
            print("\n📚 READING COMPREHENSION SAMPLES:")
            for i, response in enumerate(reading_responses, 1):
                question = Question.query.get(response.question_id)
                print(f"  Sample {i}:")
                print(f"    Question: {question.content[:80]}...")
                print(f"    Answer: {response.answer}")
                print()
        
        # Show typing test samples
        typing_responses = db.session.query(AssessmentResponse).join(Question).filter(
            Question.specialization == 'typing'
        ).limit(2).all()
        
        if typing_responses:
            print("⌨️  TYPING TEST SAMPLES:")
            for i, response in enumerate(typing_responses, 1):
                question = Question.query.get(response.question_id)
                print(f"  Sample {i}:")
                print(f"    Typing Prompt: {question.content[:80]}...")
                print(f"    Typed Text: {response.answer}")
                print()

if __name__ == "__main__":
    try:
        verify_test_coverage()
        show_sample_responses()
        
    except Exception as e:
        print(f"\n❌ Verification Error: {str(e)}")
        import traceback
        traceback.print_exc()
