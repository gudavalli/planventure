from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
Base = db.Model

def init_db(app):
    """Initialize the database with the Flask application context."""
    import models.assessment
    import models.question
    
    with app.app_context():
        db.create_all()
