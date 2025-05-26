from datetime import datetime, UTC
from flask import Blueprint, request, jsonify
from models.assessment import AssessmentTemplate, Assessment, AssessmentResponse
from models.question import Question
from models.database import db
from sqlalchemy.exc import SQLAlchemyError
from difflib import SequenceMatcher

assessments = Blueprint('assessments', __name__)

@assessments.route('/templates', methods=['POST'])
def create_template():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided'
            }), 400

        # Validate required fields
        required_fields = ['name', 'creator_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        template = AssessmentTemplate(
            name=data['name'],
            description=data.get('description'),
            percentage=data.get('percentage', 100.0),
            time_limit=data.get('time_limit'),
            creator_id=data['creator_id']
        )
        
        try:
            db.session.add(template)
            db.session.commit()
            
            response_data = {
                'id': template.id,
                'name': template.name,
                'message': 'Template created successfully'
            }
            return jsonify(response_data), 201
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({
                'error': 'Database error',
                'details': str(e)
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Invalid request',
            'details': str(e)
        }), 400

@assessments.route('/templates', methods=['GET'])
def list_templates():
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        name_search = request.args.get('name', '')
        search = request.args.get('search', '')
        
        # Build query
        query = AssessmentTemplate.query
        
        # Apply search filters
        if search:
            query = query.filter(AssessmentTemplate.name.like(f'%{search}%'))
        elif name_search:  # For backward compatibility
            query = query.filter(AssessmentTemplate.name.like(f'%{name_search}%'))
        
        # Apply pagination
        paginated_templates = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Prepare response
        templates = []
        for template in paginated_templates.items:
            # Get question count
            question_count = template.questions.count()
            
            templates.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'percentage': template.percentage,
                'time_limit': template.time_limit,
                'creator_id': template.creator_id,
                'question_count': question_count,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat()
            })
        
        # Pagination metadata
        pagination = {
            'page': paginated_templates.page,
            'per_page': paginated_templates.per_page,
            'total_pages': paginated_templates.pages,
            'total_items': paginated_templates.total,
            'has_next': paginated_templates.has_next,
            'has_prev': paginated_templates.has_prev,
            'current_page': paginated_templates.page
        }
        
        response = {
            'templates': templates,
            'pagination': pagination
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error fetching templates',
            'details': str(e)
        }), 500

@assessments.route('/templates/<int:template_id>', methods=['GET'])
def get_template_details(template_id):
    try:
        template = AssessmentTemplate.query.get_or_404(template_id)
        
        # Get question count and questions
        questions = []
        for question in template.questions:
            questions.append({
                'id': question.id,
                'text': question.text,
                'type': question.type,
                'difficulty': question.difficulty,
                'category': question.category,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation
            })
        
        response = {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'percentage': template.percentage,
            'time_limit': template.time_limit,
            'creator_id': template.creator_id,
            'question_count': len(questions),
            'questions': questions,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Error fetching template details',
            'details': str(e)
        }), 500

@assessments.route('/templates/<int:template_id>/questions', methods=['POST'])
def add_questions_to_template(template_id):
    try:
        data = request.get_json()
        if not data or 'question_ids' not in data:
            return jsonify({
                'error': 'Missing question_ids field'
            }), 400

        template = AssessmentTemplate.query.get_or_404(template_id)
        questions = []
        
        for question_id in data['question_ids']:
            question = Question.query.get(question_id)
            if not question:
                return jsonify({
                    'error': f'Question with id {question_id} not found'
                }), 404
            questions.append(question)
        
        try:
            for question in questions:
                if question not in template.questions:
                    template.questions.append(question)
            
            db.session.commit()
            return jsonify({
                'id': template.id,
                'message': 'Questions added to template successfully',
                'question_count': template.questions.count()
            }), 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({
                'error': 'Database error',
                'details': str(e)
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Invalid request',
            'details': str(e)
        }), 400

@assessments.route('/templates/<int:template_id>/analytics', methods=['GET'])
def get_template_analytics(template_id):
    try:
        template = AssessmentTemplate.query.get_or_404(template_id)
        
        # Get all assessments for this template
        assessments = Assessment.query.filter_by(template_id=template_id).all()
        
        # Calculate completion rate
        total_assessments = len(assessments)
        completed_assessments = sum(1 for a in assessments if a.status == 'completed')
        completion_rate = (completed_assessments / total_assessments) * 100 if total_assessments > 0 else 0
        
        # Calculate average score
        total_score = 0
        scored_assessments = 0
        
        for a in assessments:
            if a.status == 'completed':
                responses = AssessmentResponse.query.filter_by(assessment_id=a.id).all()
                if responses:
                    assessment_score = sum(r.score for r in responses) / len(responses)
                    total_score += assessment_score
                    scored_assessments += 1
                    
        average_score = (total_score / scored_assessments) * 100 if scored_assessments > 0 else 0
        
        analytics = {
            'template_id': template.id,
            'template_name': template.name,
            'total_assessments': total_assessments,
            'completed_assessments': completed_assessments,
            'completion_rate': round(completion_rate, 2),
            'average_score': round(average_score, 2)
        }
        
        return jsonify(analytics), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
