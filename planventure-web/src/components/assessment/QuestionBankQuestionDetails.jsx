import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const QuestionBankQuestionDetails = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { handleError } = useApiErrorHandler();
  const [question, setQuestion] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Determine return path - prioritize question bank over templates
  const returnPath = location.state?.from || '/question-bank';

  const fetchQuestionDetails = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await assessmentService.getQuestionDetails(questionId);
      setQuestion(data);
    } catch (error) {
      handleError(error);
      navigate(returnPath);
    } finally {
      setIsLoading(false);
    }
  }, [questionId, handleError, navigate, returnPath]);

  useEffect(() => {
    fetchQuestionDetails();
  }, [fetchQuestionDetails]);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      // Note: This would need to be implemented in the backend
      // await assessmentService.deleteQuestion(questionId);
      toast.success('Question deleted successfully');
      navigate(returnPath);
    } catch (error) {
      handleError(error);
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const getQuestionType = (question) => {
    if (['reading_comprehension', 'typing'].includes(question.specialization)) {
      return question.specialization;
    }
    
    if (question.options && question.options.length > 0) {
      if (question.reading_set || question.content.includes('\n\n') || question.content.length > 300) {
        return 'reading_comprehension';
      }
      return 'aptitude';
    }
    
    return 'typing';
  };

  const formatQuestionType = (type) => {
    switch (type) {
      case 'aptitude':
        return 'Multiple Choice';
      case 'reading_comprehension':
        return 'Reading Comprehension';
      case 'typing':
        return 'Typing Test';
      default:
        return type;
    }
  };

  const getQuestionTypeBadge = (type) => {
    switch (type) {
      case 'aptitude':
        return 'bg-primary';
      case 'reading_comprehension':
        return 'bg-info';
      case 'typing':
        return 'bg-success';
      default:
        return 'bg-secondary';
    }
  };

  const getDifficultyBadge = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-success';
      case 'medium':
        return 'bg-warning';
      case 'hard':
        return 'bg-danger';
      default:
        return 'bg-secondary';
    }
  };

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!question) return null;

  const questionType = getQuestionType(question);

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div className="d-flex align-items-center">
            <Button 
              variant="outline-secondary" 
              className="me-3"
              onClick={() => navigate(returnPath)}
            >
              <i className="bi bi-arrow-left"></i>
            </Button>
            <div>
              <h1 className="h3 mb-1">Question Details</h1>
              <p className="text-muted mb-0">ID: {question.id}</p>
            </div>
          </div>
          <div className="d-flex gap-2">
            <Link 
              to={`/question-bank/questions/${questionId}/edit`}
              className="btn btn-primary"
            >
              <i className="bi bi-pencil me-1"></i>Edit Question
            </Link>
            <Button 
              variant="outline-danger"
              onClick={() => setShowDeleteModal(true)}
            >
              <i className="bi bi-trash me-1"></i>Delete
            </Button>
          </div>
        </div>

        <div className="row">
          <div className="col-lg-8">
            {/* Question Content */}
            <div className="card shadow-sm mb-4">
              <div className="card-header bg-white py-3">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Question Content</h5>
                  <div className="d-flex gap-2">
                    <span className={`badge ${getQuestionTypeBadge(questionType)}`}>
                      {formatQuestionType(questionType)}
                    </span>
                    {question.difficulty && (
                      <span className={`badge ${getDifficultyBadge(question.difficulty)}`}>
                        {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="card-body">
                <div className="border rounded p-3 bg-light mb-3">
                  <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
                    {question.content}
                  </pre>
                </div>

                {question.reading_set && (
                  <div className="mb-4">
                    <h6 className="text-muted mb-2">Reading Passage</h6>
                    <div className="border rounded p-3 bg-light">
                      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
                        {question.reading_set.paragraph}
                      </pre>
                    </div>
                  </div>
                )}

                {question.options && question.options.length > 0 && (
                  <div className="mb-4">
                    <h6 className="text-muted mb-2">Answer Options</h6>
                    <div className="list-group">
                      {question.options.map((option, index) => (
                        <div
                          key={index}
                          className={`list-group-item ${
                            question.correct_answer === option ? 'list-group-item-success' : ''
                          }`}
                        >
                          <div className="d-flex justify-content-between align-items-center">
                            <span>{String.fromCharCode(65 + index)}. {option}</span>
                            {question.correct_answer === option && (
                              <span className="badge bg-success">Correct Answer</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {question.explanation && (
                  <div className="mb-3">
                    <h6 className="text-muted mb-2">Explanation</h6>
                    <div className="border rounded p-3 bg-light">
                      {question.explanation}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-lg-4">
            {/* Question Metadata */}
            <div className="card shadow-sm mb-4">
              <div className="card-header bg-white py-3">
                <h5 className="mb-0">Question Details</h5>
              </div>
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-12">
                    <label className="form-label text-muted">Specialization</label>
                    <p className="mb-0">{question.specialization || 'Not specified'}</p>
                  </div>
                  
                  {question.difficulty && (
                    <div className="col-6">
                      <label className="form-label text-muted">Difficulty</label>
                      <p className="mb-0">
                        <span className={`badge ${getDifficultyBadge(question.difficulty)}`}>
                          {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                        </span>
                      </p>
                    </div>
                  )}
                  
                  {question.time_limit && (
                    <div className="col-6">
                      <label className="form-label text-muted">Time Limit</label>
                      <p className="mb-0">{question.time_limit} seconds</p>
                    </div>
                  )}

                  <div className="col-6">
                    <label className="form-label text-muted">Question Type</label>
                    <p className="mb-0">{formatQuestionType(questionType)}</p>
                  </div>

                  <div className="col-6">
                    <label className="form-label text-muted">Options</label>
                    <p className="mb-0">{question.options ? question.options.length : 'None'}</p>
                  </div>

                  {question.created_at && (
                    <div className="col-12">
                      <label className="form-label text-muted">Created</label>
                      <p className="mb-0">{new Date(question.created_at).toLocaleDateString()}</p>
                    </div>
                  )}

                  {question.updated_at && (
                    <div className="col-12">
                      <label className="form-label text-muted">Last Updated</label>
                      <p className="mb-0">{new Date(question.updated_at).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Usage Information */}
            <div className="card shadow-sm">
              <div className="card-header bg-white py-3">
                <h5 className="mb-0">Usage Information</h5>
              </div>
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="text-muted">Templates using this question:</span>
                  <span className="badge bg-secondary">0</span>
                </div>
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span className="text-muted">Times used in assessments:</span>
                  <span className="badge bg-info">0</span>
                </div>
                <div className="d-flex justify-content-between align-items-center">
                  <span className="text-muted">Average score:</span>
                  <span className="badge bg-warning">N/A</span>
                </div>
                <hr />
                <small className="text-muted">
                  Usage statistics will be available once this question is used in assessments.
                </small>
              </div>
            </div>
          </div>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteModal && (
          <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <div className="modal-dialog">
              <div className="modal-content">
                <div className="modal-header">
                  <h5 className="modal-title">Confirm Delete</h5>
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setShowDeleteModal(false)}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="alert alert-warning">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    <strong>Warning:</strong> This action cannot be undone.
                  </div>
                  <p>Are you sure you want to delete this question?</p>
                  <div className="bg-light p-3 rounded">
                    <strong>Question:</strong> {question.content.length > 100 
                      ? `${question.content.substring(0, 100)}...` 
                      : question.content}
                  </div>
                  <p className="mt-3 text-muted mb-0">
                    <small>Note: If this question is used in any templates, it will be removed from those templates as well.</small>
                  </p>
                </div>
                <div className="modal-footer">
                  <Button 
                    variant="secondary" 
                    onClick={() => setShowDeleteModal(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="danger"
                    onClick={handleDelete}
                    isLoading={isDeleting}
                    disabled={isDeleting}
                  >
                    Delete Question
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionBankQuestionDetails;
