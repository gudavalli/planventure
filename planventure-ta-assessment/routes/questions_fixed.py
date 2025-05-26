from flask import Blueprint, request, jsonify
from models.question import Question, ReadingComprehensionSet
from models.database import db
from sqlalchemy.exc import SQLAlchemyError
import re
from difflib import SequenceMatcher
from datetime import datetime, UTC

questions = Blueprint('questions', __name__)

@questions.route('/questions', methods=['POST'])
def create_question():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['specialization', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        question = Question(
            specialization=data['specialization'],
            content=data['content'],
            options=data.get('options'),
            correct_answer=data.get('correct_answer')
        )
        
        # If it's a reading comprehension question, link it to the reading set
        if data.get('reading_set_id'):
            reading_set = ReadingComprehensionSet.query.get_or_404(data['reading_set_id'])
            reading_set.questions.append(question)
        
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question created successfully', 'id': question.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@questions.route('/questions', methods=['GET'])
def get_questions():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        specialization = request.args.get('specialization')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')  # Default sort by creation date
        order = request.args.get('order', 'desc')  # Default order descending
        simple_format = request.args.get('simple', 'true').lower() == 'true'  # Default to simple format for backward compatibility
        
        # Build query
        query = Question.query
        
        # Apply filters
        if specialization:
            query = query.filter_by(specialization=specialization)
        if search:
            search_term = f"%{search}%"
            query = query.filter(Question.content.ilike(search_term))
        
        # Apply sorting
        if order == 'desc':
            query = query.order_by(getattr(Question, sort_by).desc())
        else:
            query = query.order_by(getattr(Question, sort_by).asc())
        
        # Apply pagination
        paginated_questions = query.paginate(page=page, per_page=per_page)
        
        # Convert to list of dictionaries for JSON serialization
        questions = []
        for q in paginated_questions.items:
            # Convert correct_answer back to int if it's a numeric string
            correct_answer = q.correct_answer
            if correct_answer is not None and str(correct_answer).isdigit():
                correct_answer = int(correct_answer)
            
            question_data = {
                'id': q.id,
                'specialization': q.specialization,
                'content': q.content,
                'options': q.options,
                'correct_answer': correct_answer,
                'explanation': q.explanation,
                'difficulty': q.difficulty,
                'time_limit': q.time_limit,
                'created_at': q.created_at.isoformat(),
                'updated_at': q.updated_at.isoformat() if q.updated_at else None
            }
            # Add reading_set_id if it exists
            if hasattr(q, 'reading_sets') and q.reading_sets:
                question_data['reading_set_id'] = q.reading_sets[0].id
            
            questions.append(question_data)
        
        # Return simple format for backward compatibility
        if simple_format:
            return jsonify(questions), 200
        
        # Prepare response with pagination metadata
        response = {
            'questions': questions,
            'pagination': {
                'total_items': paginated_questions.total,
                'total_pages': paginated_questions.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': paginated_questions.has_next,
                'has_prev': paginated_questions.has_prev,
                'next_page': paginated_questions.next_num if paginated_questions.has_next else None,
                'prev_page': paginated_questions.prev_num if paginated_questions.has_prev else None
            }
        }
        
        return jsonify(response), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@questions.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    try:
        # Check for valid JSON first
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON format'}), 400
        except Exception:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        question = Question.query.get_or_404(question_id)
        
        if 'specialization' in data:
            question.specialization = data['specialization']
        if 'content' in data:
            question.content = data['content']
        if 'options' in data:
            question.options = data['options']
        if 'correct_answer' in data:
            question.correct_answer = data['correct_answer']
        if 'explanation' in data:
            question.explanation = data['explanation']
        if 'difficulty' in data:
            question.difficulty = data['difficulty']
        if 'time_limit' in data:
            question.time_limit = data['time_limit']
        if 'reading_set_id' in data:
            # Handle reading set association if needed
            pass
        
        # Explicitly update the updated_at timestamp
        question.updated_at = datetime.now(UTC)
        
        # Mark the object as modified to ensure SQLAlchemy detects the changes
        from sqlalchemy import inspect
        inspect(question).modified = True
        
        db.session.commit()
        return jsonify({'message': 'Question updated successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error during question update: {e}")
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error during question update: {e}")
        if '404' in str(e):
            return jsonify({'error': 'Question not found'}), 404
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500

@questions.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@questions.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        
        # Convert correct_answer back to int if it's a numeric string
        correct_answer = question.correct_answer
        if correct_answer is not None and str(correct_answer).isdigit():
            correct_answer = int(correct_answer)
        
        result = {
            'id': question.id,
            'specialization': question.specialization,
            'content': question.content,
            'options': question.options,
            'correct_answer': correct_answer,
            'explanation': question.explanation,
            'difficulty': question.difficulty,
            'time_limit': question.time_limit,
            'created_at': question.created_at.isoformat(),
            'updated_at': question.updated_at.isoformat() if question.updated_at else None
        }
        
        # Add reading set info if applicable
        if question.reading_sets:
            result['reading_set_id'] = question.reading_sets[0].id
        
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        if '404' in str(e):
            return jsonify({'error': 'Question not found'}), 404
        return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500

@questions.route('/reading-sets', methods=['POST'])
def create_reading_set():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['paragraph', 'specialization']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        reading_set = ReadingComprehensionSet(paragraph=data['paragraph'])
        db.session.add(reading_set)
        db.session.commit()
        
        return jsonify({
            'message': 'Reading comprehension set created successfully',
            'id': reading_set.id
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@questions.route('/reading-sets/<int:reading_set_id>', methods=['GET'])
def get_reading_set(reading_set_id):
    try:
        reading_set = ReadingComprehensionSet.query.get_or_404(reading_set_id)
        
        # Get questions associated with this reading set
        questions_data = []
        for question in reading_set.questions:
            # Convert correct_answer back to int if it's a numeric string
            correct_answer = question.correct_answer
            if correct_answer is not None and str(correct_answer).isdigit():
                correct_answer = int(correct_answer)
                
            questions_data.append({
                'id': question.id,
                'specialization': question.specialization,
                'content': question.content,
                'options': question.options,
                'correct_answer': correct_answer
            })
        
        result = {
            'id': reading_set.id,
            'paragraph': reading_set.paragraph,
            'questions': questions_data
        }
        
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@questions.route('/questions/typing/validate', methods=['POST'])
def validate_typing_response():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['question_id', 'user_response', 'time_taken_ms']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Get the question
        question = Question.query.get_or_404(data['question_id'])
        if question.specialization != 'typing':
            return jsonify({'error': 'Not a typing question'}), 400
        
        # Calculate accuracy
        target_text = question.content
        user_text = data['user_response']
        time_taken_ms = data['time_taken_ms']
        
        # Calculate accuracy using SequenceMatcher
        accuracy = SequenceMatcher(None, target_text, user_text).ratio() * 100
        
        # Calculate words per minute
        # Standard formula: (characters / 5) / (time in minutes)
        char_count = len(user_text)
        minutes = time_taken_ms / (1000 * 60)  # Convert ms to minutes
        wpm = (char_count / 5) / minutes if minutes > 0 else 0
        
        # Identify error positions
        error_positions = []
        for i, (c1, c2) in enumerate(zip(target_text, user_text)):
            if c1 != c2:
                error_positions.append(i)
                
        # If lengths differ, mark all remaining positions as errors
        for i in range(min(len(target_text), len(user_text)), max(len(target_text), len(user_text))):
            error_positions.append(i)
        
        result = {
            'accuracy_percentage': round(accuracy, 2),
            'words_per_minute': round(wpm, 2),
            'error_positions': error_positions,
            'time_taken_ms': time_taken_ms
        }
        
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
