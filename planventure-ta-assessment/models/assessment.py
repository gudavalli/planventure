from datetime import datetime, timezone, UTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from .database import db, Base

# Association table for template-question relationship
assessment_template_questions = db.Table('assessment_template_questions',
    db.Column('template_id', db.Integer, db.ForeignKey('assessment_templates.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

class AssessmentTemplate(Base):
    __tablename__ = 'assessment_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    percentage = db.Column(db.Float, nullable=False, default=100.0)  # Percentage of questions to be picked
    time_limit = db.Column(db.Integer)  # Time limit in minutes    is_active = db.Column(db.Boolean, default=True)
    creator_id = db.Column(db.Integer, nullable=False)  # ID of admin who created the template
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    questions = db.relationship('Question', secondary=assessment_template_questions, lazy='dynamic')
    assessments = db.relationship('Assessment', backref='template', lazy=True)

class Assessment(Base):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('assessment_templates.id'), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationships
    responses = db.relationship('AssessmentResponse', backref='assessment', lazy=True, overlaps="assessment")

class AssessmentResponse(Base):
    __tablename__ = 'assessment_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer = db.Column(db.Text)
    score = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    # Relationships
    question = db.relationship('Question')
