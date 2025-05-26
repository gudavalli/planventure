#!/usr/bin/env python3

# Add the current directory to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing questions.py import...")

try:
    print("1. Importing modules individually...")
    from flask import Blueprint, request, jsonify
    print("   Flask imports: OK")
    
    from models.question import Question, ReadingComprehensionSet  
    print("   Model imports: OK")
    
    from models.database import db
    print("   Database import: OK")
    
    from sqlalchemy.exc import SQLAlchemyError
    print("   SQLAlchemy import: OK")
    
    import re
    from difflib import SequenceMatcher
    from datetime import datetime, UTC
    print("   Standard library imports: OK")
    
    print("2. Creating blueprint...")
    questions = Blueprint('questions', __name__)
    print(f"   Blueprint created: {questions}")
    
    print("3. Testing module import...")
    import routes.questions
    print(f"   Module imported: {routes.questions}")
    print(f"   Module attributes: {dir(routes.questions)}")
    
    print("4. Testing blueprint import...")
    from routes.questions import questions as q_blueprint
    print(f"   Blueprint imported: {q_blueprint}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
