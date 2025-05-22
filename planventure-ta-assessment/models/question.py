from datetime import datetime, UTC
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Table
from sqlalchemy.orm import relationship
from .database import db, Base

# Association table for reading comprehension sets and questions
reading_set_questions = Table(
    'reading_set_questions',
    Base.metadata,
    db.Column('reading_set_id', db.Integer, ForeignKey('reading_comprehension_sets.id'), primary_key=True),
    db.Column('question_id', db.Integer, ForeignKey('questions.id'), primary_key=True)
)

class Question(Base):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    specialization = db.Column(db.String(50), nullable=False)  # aptitude, reading_comprehension, typing
    content = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)  # For aptitude: list of options, For reading_comprehension: might be null
    correct_answer = db.Column(db.Text)  # For aptitude: correct option, For typing: null
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    reading_sets = db.relationship('ReadingComprehensionSet', secondary=reading_set_questions, back_populates='questions')

class ReadingComprehensionSet(Base):
    __tablename__ = 'reading_comprehension_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    paragraph = db.Column(db.Text, nullable=False)
    questions = db.relationship('Question', secondary=reading_set_questions, back_populates='reading_sets')
