import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';

const ManageQuestions = () => {
  const { handleError } = useApiErrorHandler();
  
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});    const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await assessmentService.getQuestions(page, 10, filter, search);
      
      // Handle the response format with pagination data
      if (response && typeof response === 'object' && response.questions) {
        // Full format with pagination
        setQuestions(response.questions);
        setPagination(response.pagination || {});
      } else if (Array.isArray(response)) {
        // Fallback for direct array response
        setQuestions(response);
        setPagination({
          page: page,
          total_pages: 1,
          has_prev: false,
          has_next: false
        });
      } else {
        // Unexpected format
        setQuestions([]);
        setPagination({});
      }
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [page, filter, search, handleError]);
  
  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);
  
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page
    fetchQuestions();
  };
    const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setPage(1); // Reset to first page
    // The fetchQuestions will be called automatically due to useEffect dependency
  };
  
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Assessment Questions</h1>
          <Link to="/assessments/questions/create" className="btn btn-primary">
            <i className="bi bi-plus-circle me-2"></i>Create Question
          </Link>
        </div>
        
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <div className="row g-2">
              <div className="col-md-6">
                <form onSubmit={handleSearchSubmit}>
                  <div className="input-group">
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search questions..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                    <button type="submit" className="btn btn-primary">
                      <i className="bi bi-search"></i>
                    </button>
                  </div>
                </form>
              </div>
              
              <div className="col-md-6 col-lg-3 ms-auto">                <select
                  className="form-select"
                  value={filter}
                  onChange={handleFilterChange}
                >                  <option value="all">All Types</option>
                  <option value="aptitude">Multiple Choice</option>
                  <option value="reading_comprehension">Reading Comprehension</option>
                  <option value="typing">Typing Test</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        <div className="card shadow-sm">
          <div className="card-body p-0">
            {isLoading ? (
              <div className="d-flex justify-content-center p-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : questions.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover mb-0">                  <thead>
                    <tr>
                      <th style={{ width: '45%' }}>Content</th>
                      <th>Question Type</th>
                      <th>Subject Specialization</th>
                      <th>Options</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {questions.map(question => (                      <tr key={question.id}>
                        <td className="text-truncate" style={{ maxWidth: '250px' }}>
                          {question.content}
                        </td>                        <td>
                          <span className={`badge ${getQuestionTypeBadge(getQuestionType(question))}`}>
                            {formatQuestionType(getQuestionType(question))}
                          </span>
                        </td>
                        <td>
                          {getQuestionSpecialization(question) ? (
                            <span className="badge bg-secondary">
                              {getQuestionSpecialization(question)}
                            </span>
                          ) : (
                            <span className="text-muted">-</span>
                          )}
                        </td>
                        <td>
                          {question.options ? question.options.length : '-'}
                        </td>
                        <td>
                          <div className="btn-group btn-group-sm">
                            <Link 
                              to={`/assessments/questions/${question.id}`}
                              className="btn btn-outline-secondary"
                            >
                              <i className="bi bi-eye"></i>
                            </Link>
                            <Link 
                              to={`/assessments/questions/${question.id}/edit`}
                              className="btn btn-outline-primary"
                            >
                              <i className="bi bi-pencil"></i>
                            </Link>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center p-5">
                <p>No questions found</p>
              </div>
            )}            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="d-flex justify-content-between align-items-center p-3">
                <div className="text-muted small">
                  Showing {((pagination.current_page - 1) * pagination.per_page) + 1} to {Math.min(pagination.current_page * pagination.per_page, pagination.total_items)} of {pagination.total_items} questions
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
                    {(() => {
                      const currentPage = pagination.current_page;
                      const totalPages = pagination.total_pages;
                      const pages = [];
                      
                      // Show first page
                      if (currentPage > 3) {
                        pages.push(1);
                        if (currentPage > 4) {
                          pages.push('...');
                        }
                      }
                      
                      // Show pages around current page
                      const start = Math.max(1, currentPage - 2);
                      const end = Math.min(totalPages, currentPage + 2);
                      
                      for (let i = start; i <= end; i++) {
                        pages.push(i);
                      }
                      
                      // Show last page
                      if (currentPage < totalPages - 2) {
                        if (currentPage < totalPages - 3) {
                          pages.push('...');
                        }
                        pages.push(totalPages);
                      }
                      
                      return pages.map((pageNum, index) => {
                        if (pageNum === '...') {
                          return (
                            <li key={`ellipsis-${index}`} className="page-item disabled">
                              <span className="page-link">...</span>
                            </li>
                          );
                        }
                        
                        return (
                          <li key={pageNum} className={`page-item ${currentPage === pageNum ? 'active' : ''}`}>
                            <Button 
                              className="page-link" 
                              onClick={() => handlePageChange(pageNum)}
                            >
                              {pageNum}
                            </Button>
                          </li>
                        );
                      });
                    })()}
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
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to determine the actual question type based on question structure
const getQuestionType = (question) => {
  // First check if specialization field contains known type values
  if (['aptitude', 'reading_comprehension', 'typing'].includes(question.specialization)) {
    return question.specialization;
  }
  
  // For other specializations, determine type based on structure
  if (question.options && question.options.length > 0) {
    // Check if it's reading comprehension by looking for long content or reading set
    if (question.reading_set || question.content.includes('\n\n') || question.content.length > 300) {
      return 'reading_comprehension';
    }
    return 'aptitude'; // Multiple choice
  }
  
  // Default to typing for text-only questions without options
  return 'typing';
};

// Helper function to get the subject specialization
const getQuestionSpecialization = (question) => {
  // If specialization is a question type, we don't have subject specialization
  if (['aptitude', 'reading_comprehension', 'typing'].includes(question.specialization)) {
    // For 'aptitude' specialization, it's a generic aptitude question without specific subject
    return question.specialization === 'aptitude' ? 'General Aptitude' : null;
  }
  
  // Otherwise, the specialization field contains the subject domain
  // These are aptitude questions with subject specializations
  return question.specialization;
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
      return type || 'Unknown';
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

export default ManageQuestions;
