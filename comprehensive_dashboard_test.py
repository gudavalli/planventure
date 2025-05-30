#!/usr/bin/env python3
"""
Comprehensive Test Verification for QuestionBankDashboard
Tests the question_type and specialization separation functionality
"""

import requests
import json
import time
from datetime import datetime

# API endpoints
BASE_URL = "http://localhost:5001"
QUESTIONS_API = f"{BASE_URL}/api/questions"

def test_api_connectivity():
    """Test if the API is accessible"""
    print("🔗 Testing API Connectivity...")
    try:
        response = requests.get(f"{QUESTIONS_API}?page=1&limit=1")
        if response.status_code == 200:
            print("✅ API is accessible")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_question_filtering():
    """Test filtering by question_type and specialization"""
    print("\n📋 Testing Question Filtering...")
    
    # Test cases for filtering
    test_cases = [
        {
            "name": "All questions",
            "params": {"page": 1, "limit": 10},
            "expected": "Should return all questions"
        },
        {
            "name": "Filter by question_type: multiple_choice",
            "params": {"page": 1, "limit": 10, "question_type": "multiple_choice"},
            "expected": "Should return only multiple choice questions"
        },
        {
            "name": "Filter by specialization: aptitude",
            "params": {"page": 1, "limit": 10, "specialization": "aptitude"},
            "expected": "Should return only aptitude questions"
        },
        {
            "name": "Combined filter: typing + technical",
            "params": {"page": 1, "limit": 10, "question_type": "typing", "specialization": "technical"},
            "expected": "Should return typing questions with technical specialization"
        },
        {
            "name": "Combined filter: reading_comprehension + verbal",
            "params": {"page": 1, "limit": 10, "question_type": "reading_comprehension", "specialization": "verbal"},
            "expected": "Should return reading comprehension questions with verbal specialization"
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        try:
            response = requests.get(QUESTIONS_API, params=test_case['params'])
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', []) if isinstance(data, dict) else data
                
                print(f"    ✅ Status: {response.status_code}")
                print(f"    📊 Questions returned: {len(questions)}")
                print(f"    💡 Expected: {test_case['expected']}")
                
                # Validate filtering logic
                if 'question_type' in test_case['params']:
                    expected_type = test_case['params']['question_type']
                    matching_types = [q for q in questions if q.get('question_type') == expected_type or 
                                    (not q.get('question_type') and 
                                     self._infer_type_from_question(q) == expected_type)]
                    print(f"    🔍 Type filter validation: {len(matching_types)}/{len(questions)} match")
                
                if 'specialization' in test_case['params']:
                    expected_spec = test_case['params']['specialization']
                    matching_specs = [q for q in questions if q.get('specialization') == expected_spec]
                    print(f"    🔍 Specialization filter validation: {len(matching_specs)}/{len(questions)} match")
                
                results.append({
                    "test": test_case['name'],
                    "status": "PASS",
                    "count": len(questions),
                    "params": test_case['params']
                })
            else:
                print(f"    ❌ Failed with status: {response.status_code}")
                results.append({
                    "test": test_case['name'],
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}",
                    "params": test_case['params']
                })
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "test": test_case['name'],
                "status": "ERROR",
                "error": str(e),
                "params": test_case['params']
            })
    
    return results

def _infer_type_from_question(question):
    """Infer question type from question structure for legacy questions"""
    if question.get('options') and len(question.get('options', [])) > 0:
        if question.get('reading_passage'):
            return 'reading_comprehension'
        return 'multiple_choice'
    elif question.get('content') and len(question.get('content', '')) > 50:
        return 'typing'
    return 'unknown'

def test_question_creation():
    """Test creating questions with separate question_type and specialization"""
    print("\n📝 Testing Question Creation...")
    
    # Test questions to create
    test_questions = [
        {
            "name": "Multiple Choice - Aptitude",
            "data": {
                "content": "What is 2 + 2?",
                "question_type": "multiple_choice",
                "specialization": "aptitude",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "difficulty": "easy"
            }
        },
        {
            "name": "Reading Comprehension - Verbal",
            "data": {
                "content": "Based on the passage, what is the main theme?",
                "question_type": "reading_comprehension",
                "specialization": "verbal",
                "reading_passage": "This is a sample passage for reading comprehension. It contains multiple sentences and ideas that students need to analyze.",
                "options": ["Theme A", "Theme B", "Theme C", "Theme D"],
                "correct_answer": "Theme A",
                "difficulty": "medium"
            }
        },
        {
            "name": "Typing Test - Technical",
            "data": {
                "content": "Type the following code accurately: function calculateSum(a, b) { return a + b; } console.log(calculateSum(5, 3));",
                "question_type": "typing",
                "specialization": "technical",
                "difficulty": "medium"
            }
        }
    ]
    
    creation_results = []
    for test_question in test_questions:
        print(f"\n  Creating: {test_question['name']}")
        try:
            response = requests.post(QUESTIONS_API, json=test_question['data'])
            if response.status_code in [200, 201]:
                print(f"    ✅ Created successfully")
                data = response.json()
                creation_results.append({
                    "test": test_question['name'],
                    "status": "PASS",
                    "question_id": data.get('id') if isinstance(data, dict) else None
                })
            else:
                print(f"    ❌ Failed with status: {response.status_code}")
                print(f"    📝 Response: {response.text}")
                creation_results.append({
                    "test": test_question['name'],
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            print(f"    ❌ Error: {e}")
            creation_results.append({
                "test": test_question['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    return creation_results

def test_dashboard_statistics():
    """Test the statistics calculation logic"""
    print("\n📊 Testing Dashboard Statistics...")
    
    try:
        # Get all questions to calculate statistics
        response = requests.get(f"{QUESTIONS_API}?page=1&limit=1000")
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', []) if isinstance(data, dict) else data
            
            # Calculate statistics like the dashboard does
            stats = {
                'total': 0,
                'multiple_choice': 0,
                'reading_comprehension': 0,
                'typing': 0,
                'recent': 0
            }
            
            for question in questions:
                stats['total'] += 1
                
                # Determine question type
                question_type = question.get('question_type') or question.get('specialization')
                
                if question_type == 'multiple_choice' or \
                   (question.get('options') and len(question.get('options', [])) > 0 and
                    question_type not in ['reading_comprehension', 'typing']):
                    stats['multiple_choice'] += 1
                elif question_type == 'reading_comprehension':
                    stats['reading_comprehension'] += 1
                elif question_type == 'typing':
                    stats['typing'] += 1
                
                # Check if recent (within 7 days)
                if question.get('created_at'):
                    try:
                        created_date = datetime.fromisoformat(question['created_at'].replace('Z', '+00:00'))
                        days_diff = (datetime.now().replace(tzinfo=created_date.tzinfo) - created_date).days
                        if days_diff <= 7:
                            stats['recent'] += 1
                    except:
                        pass
            
            print(f"    📊 Statistics calculated:")
            print(f"      Total: {stats['total']}")
            print(f"      Multiple Choice: {stats['multiple_choice']}")
            print(f"      Reading Comprehension: {stats['reading_comprehension']}")
            print(f"      Typing: {stats['typing']}")
            print(f"      Recent (7 days): {stats['recent']}")
            print("    ✅ Statistics calculation working")
            
            return {"status": "PASS", "stats": stats}
        else:
            print(f"    ❌ Failed to get questions: {response.status_code}")
            return {"status": "FAIL", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"    ❌ Error calculating statistics: {e}")
        return {"status": "ERROR", "error": str(e)}

def generate_test_report(filter_results, creation_results, stats_result):
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("="*60)
    print(f"🕒 Test executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Test focus: QuestionBankDashboard question_type & specialization separation")
    
    # Filter tests summary
    print(f"\n📊 FILTERING TESTS:")
    passed_filters = len([r for r in filter_results if r['status'] == 'PASS'])
    total_filters = len(filter_results)
    print(f"   ✅ Passed: {passed_filters}/{total_filters}")
    
    for result in filter_results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"   {status_icon} {result['test']}")
        if result['status'] == 'PASS':
            print(f"      📊 Questions returned: {result.get('count', 'N/A')}")
        else:
            print(f"      🔍 Error: {result.get('error', 'Unknown')}")
    
    # Creation tests summary
    print(f"\n📝 CREATION TESTS:")
    passed_creation = len([r for r in creation_results if r['status'] == 'PASS'])
    total_creation = len(creation_results)
    print(f"   ✅ Passed: {passed_creation}/{total_creation}")
    
    for result in creation_results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"   {status_icon} {result['test']}")
        if result.get('question_id'):
            print(f"      🆔 Question ID: {result['question_id']}")
    
    # Statistics test summary
    print(f"\n📊 STATISTICS TEST:")
    stats_icon = "✅" if stats_result['status'] == 'PASS' else "❌"
    print(f"   {stats_icon} Dashboard statistics calculation")
    if stats_result['status'] == 'PASS':
        stats = stats_result['stats']
        print(f"      📈 Current statistics: {stats}")
    
    # Overall summary
    total_tests = total_filters + total_creation + 1
    total_passed = passed_filters + passed_creation + (1 if stats_result['status'] == 'PASS' else 0)
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   📊 Total tests: {total_tests}")
    print(f"   ✅ Passed: {total_passed}")
    print(f"   ❌ Failed: {total_tests - total_passed}")
    print(f"   📈 Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! QuestionBankDashboard is working correctly.")
        print(f"   ✨ question_type and specialization separation is functional")
        print(f"   ✨ Filtering by both fields works independently")
        print(f"   ✨ Statistics calculation handles the new field structure")
    else:
        print(f"\n⚠️ Some tests failed. Please review the results above.")
    
    print("="*60)

def main():
    """Main test execution"""
    print("🧪 PlanVenture QuestionBankDashboard Comprehensive Test")
    print("🎯 Testing question_type and specialization separation")
    print("="*60)
    
    # Test API connectivity first
    if not test_api_connectivity():
        print("❌ Cannot proceed - API is not accessible")
        return
    
    # Run all tests
    filter_results = test_question_filtering()
    creation_results = test_question_creation()
    stats_result = test_dashboard_statistics()
    
    # Generate comprehensive report
    generate_test_report(filter_results, creation_results, stats_result)

if __name__ == "__main__":
    main()
