#!/usr/bin/env python3
"""
CI/CD Pipeline Verification Script for Assessment System
This script verifies that our GitHub Actions workflow setup is complete
"""

import os
import sys
import subprocess
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} MISSING: {file_path}")
        return False


def check_file_content(file_path, required_content, description):
    """Check if a file contains required content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {description}: Found required content")
                return True
            else:
                print(f"❌ {description}: Missing required content")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False


def main():
    """Main verification function"""
    print("🔍 CI/CD Pipeline Verification for Assessment System")
    print("=" * 60)
    
    # Change to assessment directory
    assessment_dir = Path(__file__).parent
    os.chdir(assessment_dir)
    
    success_count = 0
    total_checks = 0
    
    # 1. Check GitHub Actions workflow file
    total_checks += 1
    workflow_path = "../.github/workflows/assessment-system-tests.yml"
    if check_file_exists(workflow_path, "GitHub Actions Workflow"):
        success_count += 1
    
    # 2. Check workflow contains required jobs
    total_checks += 1
    if check_file_content(workflow_path, "jobs:", "Workflow Jobs Configuration"):
        success_count += 1
    
    # 3. Check pytest configuration
    total_checks += 1
    if check_file_exists("pytest.ini", "Pytest Configuration"):
        success_count += 1
    
    # 4. Check requirements files
    total_checks += 1
    if check_file_exists("requirements.txt", "Core Requirements"):
        success_count += 1
    
    total_checks += 1
    if check_file_exists("requirements-dev.txt", "Development Requirements"):
        success_count += 1
    
    # 5. Check security configuration
    total_checks += 1
    if check_file_exists(".bandit", "Security Scan Configuration"):
        success_count += 1
    
    # 6. Check code formatting configuration
    total_checks += 1
    if check_file_exists("pyproject.toml", "Code Formatting Configuration"):
        success_count += 1
    
    # 7. Check test files
    test_files = [
        ("tests/test_delete_endpoint_unit.py", "DELETE Endpoint Unit Tests"),
        ("tests/test_error_handling_comprehensive.py", "Error Handling Tests"),
        ("tests/conftest.py", "Test Configuration"),
    ]
    
    for test_file, description in test_files:
        total_checks += 1
        if check_file_exists(test_file, description):
            success_count += 1
    
    # 8. Check core application files
    app_files = [
        ("app.py", "Flask Application"),
        ("init_db.py", "Database Initialization"),
        ("routes/assessments.py", "Assessment Routes"),
        ("models/database.py", "Database Models"),
    ]
    
    for app_file, description in app_files:
        total_checks += 1
        if check_file_exists(app_file, description):
            success_count += 1
    
    # 9. Check CI/CD documentation
    total_checks += 1
    if check_file_exists("CI_CD_README.md", "CI/CD Documentation"):
        success_count += 1
    
    # 10. Try to run a simple import test
    total_checks += 1
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.insert(0, '.'); from app import create_app; print('Import successful')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Application Import Test: Success")
            success_count += 1
        else:
            print(f"❌ Application Import Test: Failed - {result.stderr}")
    except Exception as e:
        print(f"❌ Application Import Test: Error - {e}")
    
    # 11. Check if database can be initialized
    total_checks += 1
    try:
        result = subprocess.run([
            sys.executable, "init_db.py"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Database Initialization Test: Success")
            success_count += 1
        else:
            print(f"❌ Database Initialization Test: Failed - {result.stderr}")
    except Exception as e:
        print(f"❌ Database Initialization Test: Error - {e}")
    
    # 12. Check if core tests can be discovered
    total_checks += 1
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--collect-only", "-q", 
            "tests/test_delete_endpoint_unit.py"
        ], capture_output=True, text=True, timeout=10)
        
        if "collected" in result.stdout and result.returncode == 0:
            print("✅ Test Discovery: Success")
            success_count += 1
        else:
            print(f"❌ Test Discovery: Failed - {result.stderr}")
    except Exception as e:
        print(f"❌ Test Discovery: Error - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 CI/CD Pipeline Verification Summary")
    print(f"✅ Passed: {success_count}/{total_checks} checks")
    print(f"❌ Failed: {total_checks - success_count}/{total_checks} checks")
    
    if success_count == total_checks:
        print("\n🎉 CI/CD Pipeline is ready for deployment!")
        print("\nNext steps:")
        print("1. Push changes to GitHub to trigger the workflow")
        print("2. Monitor GitHub Actions for first pipeline run")
        print("3. Check coverage reports and fix any issues")
        return 0
    else:
        print(f"\n⚠️  CI/CD Pipeline has {total_checks - success_count} issues to resolve")
        print("\nPlease fix the failed checks before deploying")
        return 1


if __name__ == "__main__":
    sys.exit(main())
