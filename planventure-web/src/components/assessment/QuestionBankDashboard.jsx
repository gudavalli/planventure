import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const QuestionBankDashboard = () => {
  const { handleError } = useApiErrorHandler();
  
  // State for questions
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  
  // State for statistics
  const [stats, setStats] = useState({
    total: 0,
    aptitude: 0,
    reading_comprehension: 0,
    typing: 0,
    recent: 0
  });

  const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await assessmentService.getQuestions(page, 12, filter, search);
      
      if (response && typeof response === 'object' && response.questions) {
        setQuestions(response.questions);
        setPagination(response.pagination || {});
      } else if (Array.isArray(response)) {
        setQuestions(response);
        setPagination({
          current_page: page,
          total_pages: 1,
          has_prev: false,
          has_next: false
        });
      } else {
        setQuestions([]);
        setPagination({});
      }
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [page, filter, search, handleError]);

  const fetchStats = useCallback(async () => {
    try {
      // Fetch questions by type to calculate statistics
      const allQuestions = await assessmentService.getQuestions(1, 1000, 'all', '');
      const questionsList = allQuestions.questions || allQuestions || [];
      
      const stats = questionsList.reduce((acc, question) => {
        acc.total++;
        
        if (question.specialization === 'aptitude' || 
            (question.options && question.options.length > 0 && question.specialization !== 'reading_comprehension' && question.specialization !== 'typing')) {
          acc.aptitude++;
        } else if (question.specialization === 'reading_comprehension') {
          acc.reading_comprehension++;
        } else if (question.specialization === 'typing') {
          acc.typing++;
        }
        
        // Count recent questions (created in last 7 days)
        if (question.created_at) {
          const created = new Date(question.created_at);
          const weekAgo = new Date();
          weekAgo.setDate(weekAgo.getDate() - 7);
          if (created > weekAgo) {
            acc.recent++;
          }
        }
        
        return acc;
      }, { total: 0, aptitude: 0, reading_comprehension: 0, typing: 0, recent: 0 });
      
      setStats(stats);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchQuestions();
    fetchStats();
  }, [fetchQuestions, fetchStats]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchQuestions();
  };

  const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setPage(1);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
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

  const getQuestionSpecialization = (question) => {
    if (['reading_comprehension', 'typing'].includes(question.specialization)) {
      return 'General Aptitude';
    }
    return question.specialization;
  };

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 className="h3 mb-1">Question Bank</h1>
            <p className="text-muted mb-0">Centralized question management and organization</p>
          </div>
          <div>
            <Link to="/question-bank/create" className="btn btn-primary">
              <i className="bi bi-plus-circle me-2"></i>Create Question
            </Link>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="row mb-4">
          <div className="col-md-3">
            <div className="card bg-primary text-white">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h4 className="card-title mb-1">{stats.total}</h4>
                    <p className="card-text mb-0">Total Questions</p>
                  </div>
                  <i className="bi bi-question-circle display-6"></i>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-info text-white">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h4 className="card-title mb-1">{stats.aptitude}</h4>
                    <p className="card-text mb-0">Multiple Choice</p>
                  </div>
                  <i className="bi bi-list-check display-6"></i>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-success text-white">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h4 className="card-title mb-1">{stats.reading_comprehension}</h4>
                    <p className="card-text mb-0">Reading</p>
                  </div>
                  <i className="bi bi-book display-6"></i>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card bg-warning text-white">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h4 className="card-title mb-1">{stats.typing}</h4>
                    <p className="card-text mb-0">Typing Tests</p>
                  </div>
                  <i className="bi bi-keyboard display-6"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search and Filter Controls */}
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <div className="row g-2">
              <div className="col-md-6">
                <form onSubmit={handleSearchSubmit}>
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search questions by content, type, or subject..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary">
                      <i className="bi bi-search"></i>
                    </button>
                  </div>
                </form>
              </div>
              
              <div className="col-md-3">
                <select
                  className="form-select"
                  value={filter}
                  onChange={handleFilterChange}
                >
                  <option value="all">All Question Types</option>
                  <option value="aptitude">Multiple Choice</option>
                  <option value="reading_comprehension">Reading Comprehension</option>
                  <option value="typing">Typing Test</option>
                </select>
              </div>

              <div className="col-md-3">
                <div className="d-flex gap-2">
                  <Link to="/question-bank/bulk-import" className="btn btn-outline-secondary">
                    <i className="bi bi-upload me-1"></i>Import
                  </Link>
                  <Button variant="outline-secondary">
                    <i className="bi bi-download me-1"></i>Export
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Questions Grid */}
        <div className="card shadow-sm">
          <div className="card-body p-0">
            {isLoading ? (
              <div className="d-flex justify-content-center p-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : questions.length > 0 ? (
              <>
                <div className="row g-3 p-3">
                  {questions.map(question => (
                    <div key={question.id} className="col-md-6 col-lg-4">
                      <div className="card h-100 border">
                        <div className="card-body d-flex flex-column">
                          <div className="d-flex justify-content-between align-items-start mb-2">
                            <span className={`badge ${getQuestionTypeBadge(getQuestionType(question))}`}>
                              {formatQuestionType(getQuestionType(question))}
                            </span>
                            {getQuestionSpecialization(question) && (
                              <span className="badge bg-secondary text-truncate ms-1" style={{ maxWidth: '100px' }}>
                                {getQuestionSpecialization(question)}
                              </span>
                            )}
                          </div>
                          
                          <p className="card-text flex-grow-1 text-truncate-3" style={{
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            minHeight: '4.5rem'
                          }}>
                            {question.content}
                          </p>
                          
                          <div className="d-flex justify-content-between align-items-center mt-auto pt-2">
                            <small className="text-muted">
                              {question.options ? `${question.options.length} options` : 'Text response'}
                            </small>
                            <div className="btn-group btn-group-sm">
                              <Link 
                                to={`/question-bank/questions/${question.id}`}
                                className="btn btn-outline-secondary"
                                title="View Details"
                              >
                                <i className="bi bi-eye"></i>
                              </Link>
                              <Link 
                                to={`/question-bank/questions/${question.id}/edit`}
                                className="btn btn-outline-primary"
                                title="Edit Question"
                              >
                                <i className="bi bi-pencil"></i>
                              </Link>
                              <Button 
                                variant="outline-danger"
                                size="sm"
                                title="Delete Question"
                              >
                                <i className="bi bi-trash"></i>
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {pagination && pagination.total_pages > 1 && (
                  <div className="d-flex justify-content-between align-items-center p-3 border-top">
                    <div className="text-muted small">
                      Showing {((pagination.current_page - 1) * 12) + 1} to {Math.min(pagination.current_page * 12, pagination.total_items || questions.length)} of {pagination.total_items || questions.length} questions
                    </div>
                    <nav aria-label="Question pagination">
                      <ul className="pagination mb-0">
                        <li className={`page-item ${!pagination.has_prev ? 'disabled' : ''}`}>
                          <Button 
                            className="page-link" 
                            onClick={() => handlePageChange(pagination.current_page - 1)}
                            disabled={!pagination.has_prev}
                          >
                            Previous
                          </Button>
                        </li>
                        {[...Array(Math.min(pagination.total_pages, 5)).keys()].map(i => {
                          const pageNum = i + 1;
                          return (
                            <li key={pageNum} className={`page-item ${pagination.current_page === pageNum ? 'active' : ''}`}>
                              <Button 
                                className="page-link" 
                                onClick={() => handlePageChange(pageNum)}
                              >
                                {pageNum}
                              </Button>
                            </li>
                          );
                        })}
                        <li className={`page-item ${!pagination.has_next ? 'disabled' : ''}`}>
                          <Button 
                            className="page-link" 
                            onClick={() => handlePageChange(pagination.current_page + 1)}
                            disabled={!pagination.has_next}
                          >
                            Next
                          </Button>
                        </li>
                      </ul>
                    </nav>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center p-5">
                <i className="bi bi-question-circle text-muted" style={{ fontSize: '3rem' }}></i>
                <h4 className="mt-3 text-muted">No Questions Found</h4>
                <p className="text-muted mb-3">
                  {search || filter !== 'all' 
                    ? 'Try adjusting your search or filter criteria.' 
                    : 'Start building your question bank by creating your first question.'
                  }
                </p>
                <Link to="/question-bank/create" className="btn btn-primary">
                  <i className="bi bi-plus-circle me-2"></i>Create First Question
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="row mt-4">
          <div className="col-md-6">
            <div className="card bg-light">
              <div className="card-body text-center">
                <i className="bi bi-lightning text-primary" style={{ fontSize: '2rem' }}></i>
                <h5 className="mt-2">Quick Import</h5>
                <p className="text-muted">Import questions from CSV or Excel files</p>
                <Link to="/question-bank/bulk-import" className="btn btn-outline-primary">
                  Import Questions
                </Link>
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card bg-light">
              <div className="card-body text-center">
                <i className="bi bi-collection text-success" style={{ fontSize: '2rem' }}></i>
                <h5 className="mt-2">Question Categories</h5>
                <p className="text-muted">Organize questions by subjects and topics</p>
                <Link to="/question-bank/categories" className="btn btn-outline-success">
                  Manage Categories
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionBankDashboard;
