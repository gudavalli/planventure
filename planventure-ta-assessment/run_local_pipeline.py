#!/usr/bin/env python3
"""
Local CI/CD simulation script for the assessment system
This script simulates the GitHub Actions workflow locally
"""

import subprocess
import sys
import os
import time
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def run_command(command, description, continue_on_error=False):
    """Run a command and return success status"""
    print(f"\n{Colors.BLUE}🔄 {description}{Colors.ENDC}")
    print(f"Running: {command}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        duration = time.time() - start_time
        print(f"{Colors.GREEN}✅ {description} completed in {duration:.2f}s{Colors.ENDC}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        if continue_on_error:
            print(f"{Colors.YELLOW}⚠️  {description} failed in {duration:.2f}s (continuing){Colors.ENDC}")
            if e.stdout:
                print(f"Output: {e.stdout}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
        else:
            print(f"{Colors.RED}❌ {description} failed in {duration:.2f}s{Colors.ENDC}")
            if e.stdout:
                print(f"Output: {e.stdout}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False


def main():
    """Main CI/CD simulation function"""
    print(f"{Colors.BOLD}🚀 Starting Local CI/CD Pipeline for Assessment System{Colors.ENDC}")
    
    # Change to assessment directory
    os.chdir(Path(__file__).parent)
    
    # Track results
    results = {}
    
    # 1. Install dependencies
    results['dependencies'] = run_command(
        "pip install -r requirements.txt",
        "Installing core dependencies"
    )
    
    results['dev_dependencies'] = run_command(
        "pip install -r requirements-dev.txt",
        "Installing development dependencies",
        continue_on_error=True
    )
    
    # 2. Code quality checks
    results['flake8_syntax'] = run_command(
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Checking for syntax errors with flake8"
    )
    
    results['flake8_quality'] = run_command(
        "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
        "Running flake8 code quality check",
        continue_on_error=True
    )
    
    results['black_check'] = run_command(
        "black --check --diff .",
        "Checking code formatting with black",
        continue_on_error=True
    )
    
    results['isort_check'] = run_command(
        "isort --check-only --diff .",
        "Checking import sorting with isort",
        continue_on_error=True
    )
    
    # 3. Security checks
    results['safety_check'] = run_command(
        "safety check",
        "Checking for security vulnerabilities in dependencies",
        continue_on_error=True
    )
    
    results['bandit_scan'] = run_command(
        "bandit -r . -f txt",
        "Running bandit security scan",
        continue_on_error=True
    )
    
    # 4. Database initialization
    results['db_init'] = run_command(
        "python init_db.py",
        "Initializing database"
    )
    
    # 5. Run tests
    results['unit_tests'] = run_command(
        "python -m pytest tests/ -v --tb=short",
        "Running unit tests"
    )
    
    results['delete_endpoint_tests'] = run_command(
        "python -m pytest tests/test_delete_endpoint_unit.py -v",
        "Running DELETE endpoint specific tests"
    )
    
    results['error_handling_tests'] = run_command(
        "python -m pytest tests/test_error_handling_comprehensive.py -v",
        "Running comprehensive error handling tests"
    )
    
    results['integration_tests'] = run_command(
        "python -m pytest tests/test_integration.py -v",
        "Running integration tests",
        continue_on_error=True
    )
    
    results['performance_tests'] = run_command(
        "python -m pytest tests/test_performance.py -v",
        "Running performance tests",
        continue_on_error=True
    )
    
    # 6. Coverage report
    results['coverage'] = run_command(
        "python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html",
        "Generating coverage report",
        continue_on_error=True
    )
    
    # Print summary
    print(f"\n{Colors.BOLD}📊 Pipeline Summary{Colors.ENDC}")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for step, success in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.ENDC}" if success else f"{Colors.RED}❌ FAIL{Colors.ENDC}"
        print(f"{step:30} {status}")
    
    print("=" * 50)
    print(f"Total: {passed}/{total} steps passed")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All pipeline steps completed successfully!{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  Pipeline completed with {total - passed} warning(s)/failure(s){Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
