import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import Navigation from '../Navigation';
import Button from '../Button';
import { Modal } from 'react-bootstrap';
import toast from 'react-hot-toast';

const QuestionBankQuestionView = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const [question, setQuestion] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);  const { handleError } = useApiErrorHandler();

  const fetchQuestion = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await assessmentService.getQuestionDetails(questionId);
      setQuestion(data);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [questionId, handleError]);

  useEffect(() => {
    fetchQuestion();
  }, [fetchQuestion]);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await assessmentService.deleteQuestion(questionId);
      toast.success('Question deleted successfully');
      navigate('/question-bank');
    } catch (error) {
      handleError(error);
    } finally {
      setIsDeleting(false);
    }
  };

  const getDifficultyBadgeClass = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'badge bg-success';
      case 'medium': return 'badge bg-warning text-dark';
      case 'hard': return 'badge bg-danger';
      default: return 'badge bg-secondary';
    }
  };

  const getSpecializationBadgeClass = (specialization) => {
    const classes = {
      'aptitude': 'badge bg-primary',
      'verbal': 'badge bg-info',
      'quantitative': 'badge bg-warning text-dark',
      'logical': 'badge bg-success',
      'technical': 'badge bg-danger'
    };
    return classes[specialization?.toLowerCase()] || 'badge bg-secondary';
  };

  if (isLoading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container-fluid py-4">
          <div className="text-center py-5">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container-fluid py-4">
          <div className="text-center py-5">
            <i className="bi bi-exclamation-triangle fs-1 text-muted mb-3"></i>
            <h5 className="text-muted">Question not found</h5>
            <Link to="/question-bank" className="btn btn-primary">
              Back to Question Bank
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      <div className="container-fluid py-4">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <nav aria-label="breadcrumb">
                  <ol className="breadcrumb">
                    <li className="breadcrumb-item">
                      <Link to="/question-bank">Question Bank</Link>
                    </li>
                    <li className="breadcrumb-item active" aria-current="page">
                      Question Details
                    </li>
                  </ol>
                </nav>
                <h1 className="h3 mb-0">Question Details</h1>
              </div>
              <div className="btn-group">
                <Link
                  to={`/question-bank/${questionId}/edit`}
                  className="btn btn-outline-primary"
                >
                  <i className="bi bi-pencil me-2"></i>
                  Edit Question
                </Link>
                <button
                  type="button"
                  className="btn btn-outline-danger"
                  onClick={() => setDeleteModalOpen(true)}
                >
                  <i className="bi bi-trash me-2"></i>
                  Delete
                </button>
              </div>
            </div>

            {/* Question Card */}
            <div className="card">
              <div className="card-header">
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">Question Information</h5>
                  <div>
                    <span className={getSpecializationBadgeClass(question.specialization)} style={{ marginRight: '8px' }}>
                      {question.specialization || 'N/A'}
                    </span>
                    <span className={getDifficultyBadgeClass(question.difficulty)}>
                      {question.difficulty || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="card-body">
                {/* Question Content */}
                <div className="mb-4">
                  <h6 className="text-muted mb-2">Question Content</h6>
                  <div className="bg-light p-3 rounded">
                    <p className="mb-0 fs-5">{question.content}</p>
                  </div>
                </div>

                {/* Options (if multiple choice) */}
                {question.options && question.options.length > 0 && (
                  <div className="mb-4">
                    <h6 className="text-muted mb-2">Answer Options</h6>
                    <div className="row">
                      {question.options.map((option, index) => {
                        const isCorrect = question.correct_answer === index || question.correct_answer === option;
                        return (
                          <div key={index} className="col-md-6 mb-2">
                            <div className={`p-3 rounded border ${isCorrect ? 'bg-success bg-opacity-10 border-success' : 'bg-light'}`}>
                              <div className="d-flex align-items-center">
                                <span className={`badge me-2 ${isCorrect ? 'bg-success' : 'bg-secondary'}`}>
                                  {String.fromCharCode(65 + index)}
                                </span>
                                <span>{option}</span>
                                {isCorrect && (
                                  <i className="bi bi-check-circle-fill text-success ms-auto"></i>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Question Details Grid */}
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <h6 className="text-muted mb-1">Specialization</h6>
                      <p className="mb-0">{question.specialization || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <h6 className="text-muted mb-1">Difficulty Level</h6>
                      <p className="mb-0">{question.difficulty || 'Not specified'}</p>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <h6 className="text-muted mb-1">Time Limit</h6>
                      <p className="mb-0">
                        {question.time_limit ? `${question.time_limit} seconds` : 'Not specified'}
                      </p>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <h6 className="text-muted mb-1">Question Type</h6>
                      <p className="mb-0">
                        {question.options && question.options.length > 0 
                          ? 'Multiple Choice' 
                          : 'Open-ended'
                        }
                      </p>
                    </div>
                  </div>
                </div>

                {/* Explanation */}
                {question.explanation && (
                  <div className="mb-4">
                    <h6 className="text-muted mb-2">Explanation</h6>
                    <div className="bg-info bg-opacity-10 p-3 rounded border border-info">
                      <p className="mb-0">{question.explanation}</p>
                    </div>
                  </div>
                )}

                {/* Question Usage */}
                <div className="mt-4 pt-4 border-top">
                  <h6 className="text-muted mb-3">Question Usage</h6>
                  <div className="row">
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <i className="bi bi-file-text fs-2 text-primary mb-2"></i>
                        <h6 className="mb-1">Templates</h6>
                        <p className="text-muted mb-0 small">Used in 0 templates</p>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <i className="bi bi-graph-up fs-2 text-success mb-2"></i>
                        <h6 className="mb-1">Assessments</h6>
                        <p className="text-muted mb-0 small">Used in 0 assessments</p>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="text-center p-3 bg-light rounded">
                        <i className="bi bi-people fs-2 text-warning mb-2"></i>
                        <h6 className="mb-1">Responses</h6>
                        <p className="text-muted mb-0 small">0 total responses</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="card-footer">
                <div className="d-flex justify-content-between align-items-center">
                  <Link to="/question-bank" className="btn btn-outline-secondary">
                    <i className="bi bi-arrow-left me-2"></i>
                    Back to Question Bank
                  </Link>
                  <div>
                    <Link
                      to={`/question-bank/${questionId}/edit`}
                      className="btn btn-primary me-2"
                    >
                      <i className="bi bi-pencil me-2"></i>
                      Edit Question
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>      {/* Delete Confirmation Modal */}
      <Modal
        show={deleteModalOpen}
        onHide={() => setDeleteModalOpen(false)}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Confirm Deletion</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete this question?</p>
          <div className="bg-light p-3 rounded">
            <strong>Question:</strong> {question.content}
          </div>
          <p className="text-danger mt-3 mb-0">
            <i className="bi bi-exclamation-triangle me-2"></i>
            This action cannot be undone.
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => setDeleteModalOpen(false)}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleDelete}
            isLoading={isDeleting}
          >
            Delete Question
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default QuestionBankQuestionView;
