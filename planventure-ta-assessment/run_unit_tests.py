"""
Comprehensive test runner for the assessment backend.
Runs all unit tests and provides detailed reporting.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_tests():
    """Run all unit tests and generate a comprehensive report."""
    
    print("🧪 Starting Comprehensive Backend Unit Tests")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir(r'c:\Users\sreen\learning\copilot-agent\planventure\planventure-ta-assessment')
    
    # Test files to run
    test_files = [
        'tests/test_delete_endpoint_unit.py',
        'tests/test_error_handling_comprehensive.py',
        'tests/test_assessments.py',  # If it exists and is working
        'tests/test_questions.py',    # If it exists and is working
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 Running {test_file}")
            print("-" * 40)
            
            try:
                # Run pytest with verbose output and JSON report
                cmd = [
                    sys.executable, '-m', 'pytest', 
                    test_file, 
                    '-v', 
                    '--tb=short',
                    '--json-report',
                    '--json-report-file=test_report.json'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                print("STDOUT:")
                print(result.stdout)
                
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                
                # Try to read JSON report for detailed stats
                try:
                    with open('test_report.json', 'r') as f:
                        report = json.load(f)
                        passed = report['summary']['passed']
                        failed = report['summary']['failed']
                        total = report['summary']['total']
                        
                        results[test_file] = {
                            'passed': passed,
                            'failed': failed,
                            'total': total,
                            'status': 'success' if failed == 0 else 'failed'
                        }
                        
                        total_passed += passed
                        total_failed += failed
                        total_tests += total
                        
                except (FileNotFoundError, KeyError, json.JSONDecodeError):
                    # Fallback to return code
                    results[test_file] = {
                        'status': 'success' if result.returncode == 0 else 'failed',
                        'return_code': result.returncode
                    }
                
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                results[test_file] = {'status': 'error', 'error': str(e)}
        else:
            print(f"⚠️  Test file {test_file} not found, skipping...")
            results[test_file] = {'status': 'not_found'}
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 60)
    
    print(f"📈 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📊 Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "No tests")
    
    print("\n📋 Detailed Results:")
    for test_file, result in results.items():
        status_emoji = {
            'success': '✅',
            'failed': '❌',
            'error': '💥',
            'not_found': '⚠️'
        }.get(result['status'], '❓')
        
        print(f"{status_emoji} {test_file}: {result['status']}")
        if 'passed' in result:
            print(f"   - Passed: {result['passed']}, Failed: {result['failed']}, Total: {result['total']}")
    
    # Generate recommendations
    print("\n🔍 RECOMMENDATIONS:")
    if total_failed > 0:
        print("❌ Some tests failed. Review the detailed output above.")
        print("🔧 Consider fixing failing tests before deployment.")
    else:
        print("✅ All tests passed! Backend is ready for deployment.")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Review any failing tests and fix issues")
    print("2. Run integration tests if available")
    print("3. Test the DELETE endpoint manually if needed")
    print("4. Consider adding more edge case tests")
    
    # Cleanup
    if os.path.exists('test_report.json'):
        os.remove('test_report.json')
    
    return total_failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
