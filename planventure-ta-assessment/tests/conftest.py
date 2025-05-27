import pytest
import os
import sys
import json

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from models.database import db

@pytest.fixture(scope='function')
def app():
    """Create application for the tests."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    with app.app_context():
        client = app.test_client()
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def setup_database(app):
    """Set up a clean database for each test."""
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()

def create_test_question(client):
    """Helper function to create a test question"""
    import time
    timestamp = int(time.time() * 1000)  # Use millisecond timestamp for uniqueness
    data = {
        'specialization': 'aptitude',
        'content': f'What is 2+2? {timestamp}',  # Make content unique
        'options': ['3', '4', '5', '6'],
        'correct_answer': '4'
    }
    response = client.post('/api/questions', 
                         data=json.dumps(data),
                         content_type='application/json')
    return json.loads(response.data)

def create_test_template(client):
    """Helper function to create a test template"""
    import time
    timestamp = int(time.time() * 1000)  # Use millisecond timestamp for uniqueness
    data = {
        'name': f'Test Template {timestamp}',  # Make name unique
        'description': 'Test Description',
        'percentage': 100.0,
        'time_limit': 60,
        'creator_id': 1
    }
    response = client.post('/api/templates',
                         data=json.dumps(data),
                         content_type='application/json')
    return json.loads(response.data)
