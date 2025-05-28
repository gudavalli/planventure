import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import Navigation from '../Navigation';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';

const ViewQuestionDetails = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { handleError } = useApiErrorHandler();
  const [question, setQuestion] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchQuestionDetails = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await assessmentService.getQuestionDetails(questionId);
      setQuestion(data);
    } catch (error) {
      handleError(error);
      navigate('/assessments/questions');
    } finally {
      setIsLoading(false);
    }
  }, [questionId, handleError, navigate]);

  useEffect(() => {
    fetchQuestionDetails();
  }, [fetchQuestionDetails]);

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

  const formatQuestionType = (type) => {
    switch (type) {
      case 'aptitude':
        return 'Multiple Choice';
      case 'reading_comprehension':
        return 'Reading';
      case 'typing':
        return 'Typing';
      default:
        return type;
    }
  };

  if (isLoading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container py-4">
          <div className="d-flex justify-content-center p-5">
            <div className="spinner-border text-primary" role="status">
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
        <div className="container py-4">
          <div className="alert alert-danger">Question not found</div>
          <Link to="/assessments/questions" className="btn btn-primary">
            Back to Questions
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Question Details</h1>
          <div>            <Link 
              to={location.state?.from || "/assessments/questions"}
              className="btn btn-outline-secondary me-2"
            >
              <i className="bi bi-arrow-left me-1"></i>Back            </Link><Link to={`/assessments/questions/${questionId}/edit?returnTo=${encodeURIComponent(location.state?.from || location.pathname)}`} className="btn btn-primary">
              <i className="bi bi-pencil me-1"></i>Edit Question
            </Link>
          </div>
        </div>

        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <div className="mb-4">
              <div className="d-flex justify-content-between mb-2">
                <div>
                  <span className={`badge ${getQuestionTypeBadge(question.type)} me-2`}>
                    {formatQuestionType(question.type)}
                  </span>
                  {question.specialization && (
                    <span className="badge bg-secondary">
                      {question.specialization}
                    </span>
                  )}
                </div>
                <small className="text-muted">ID: {question.id}</small>
              </div>
              <h4 className="card-title">Question Content</h4>
              <div className="border rounded p-3 bg-light">
                {question.content}
              </div>
            </div>

            {question.reading_set && (
              <div className="mb-4">
                <h4 className="card-title">Reading Passage</h4>
                <div className="border rounded p-3 bg-light">
                  {question.reading_set.paragraph}
                </div>
              </div>
            )}

            {question.options && question.options.length > 0 && (
              <div className="mb-4">
                <h4 className="card-title">Options</h4>
                <ul className="list-group">
                  {question.options.map((option, index) => (
                    <li
                      key={index}
                      className={`list-group-item ${
                        question.correct_answer === option ? 'list-group-item-success' : ''
                      }`}
                    >
                      {option}
                      {question.correct_answer === option && (
                        <span className="badge bg-success ms-2">Correct Answer</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="text-muted">
              <div><strong>Created:</strong> {new Date(question.created_at).toLocaleString()}</div>
              <div><strong>Last Updated:</strong> {new Date(question.updated_at).toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewQuestionDetails;
