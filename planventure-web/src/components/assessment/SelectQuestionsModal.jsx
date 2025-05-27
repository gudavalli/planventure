import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Modal from 'react-bootstrap/Modal';
import Navigation from '../Navigation';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const SelectQuestionsModal = ({ show, onHide, templateId, onQuestionsAdded }) => {
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [selectedQuestionIds, setSelectedQuestionIds] = useState([]);
  const [isAdding, setIsAdding] = useState(false);
  
  const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await assessmentService.getQuestions(page, 10, filter, search);
      
      // Handle the response format with pagination data
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
  
  useEffect(() => {
    if (show) {
      fetchQuestions();
    }
  }, [show, fetchQuestions]);
  
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1); // Reset to first page
    fetchQuestions();
  };
  
  const handleFilterChange = (e) => {
    setFilter(e.target.value);
    setPage(1); // Reset to first page
  };
  
  const handlePageChange = (newPage) => {
    setPage(newPage);
  };
  
  const handleCheckboxChange = (questionId) => {
    setSelectedQuestionIds(prev => {
      if (prev.includes(questionId)) {
        return prev.filter(id => id !== questionId);
      } else {
        return [...prev, questionId];
      }
    });
  };
  
  const handleAddSelectedQuestions = async () => {
    if (selectedQuestionIds.length === 0) {
      toast.error('Please select at least one question to add');
      return;
    }
    
    setIsAdding(true);
    try {
      await assessmentService.addQuestionsToTemplate(templateId, selectedQuestionIds);
      toast.success(`${selectedQuestionIds.length} question(s) added to template successfully`);
      onQuestionsAdded();
      onHide();
    } catch (error) {
      handleError(error);
    } finally {
      setIsAdding(false);
    }
  };
  
  const getQuestionType = (question) => {
    // If specialization field contains known type values, use them
    if (['reading_comprehension', 'typing'].includes(question.specialization)) {
      return question.specialization;
    }
    
    // For all other specializations (including 'aptitude' and subject names), determine type based on structure
    if (question.options && question.options.length > 0) {
      // Check if it's reading comprehension by looking for long content or reading set
      if (question.reading_set || question.content.includes('\n\n') || question.content.length > 300) {
        return 'reading_comprehension';
      }
      return 'aptitude'; // Multiple choice question with options
    }
    
    // Default to typing for text-only questions without options
    return 'typing';
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
  
  const getQuestionSpecialization = (question) => {
    const questionType = getQuestionType(question);
    
    // Only aptitude questions have subject specializations
    if (questionType !== 'aptitude') {
      return null;
    }
    
    // If specialization is just 'aptitude', it's a general aptitude question
    if (question.specialization === 'aptitude') {
      return 'General Aptitude';
    }
    
    // If specialization contains a specific question type, it's general aptitude
    if (['reading_comprehension', 'typing'].includes(question.specialization)) {
      return 'General Aptitude';
    }
    
    // Otherwise, the specialization field contains the subject domain (JavaScript, React, CSS, etc.)
    return question.specialization;
  };

  return (
    <Modal show={show} onHide={onHide} size="xl">
      <Modal.Header closeButton>
        <Modal.Title>Add Questions to Template</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <div className="mb-3">
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
            
            <div className="col-md-6 col-lg-3 ms-auto">
              <select
                className="form-select"
                value={filter}
                onChange={handleFilterChange}
              >
                <option value="all">All Types</option>
                <option value="aptitude">Multiple Choice</option>
                <option value="reading_comprehension">Reading Comprehension</option>
                <option value="typing">Typing Test</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="table-responsive" style={{ maxHeight: '60vh' }}>
          {isLoading ? (
            <div className="d-flex justify-content-center p-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : questions.length > 0 ? (
            <table className="table table-hover mb-0">
              <thead>
                <tr>
                  <th style={{ width: '50px' }}></th>
                  <th>Content</th>
                  <th>Type</th>
                  <th>Subject</th>
                  <th>Options</th>
                </tr>
              </thead>
              <tbody>
                {questions.map(question => (
                  <tr key={question.id}>
                    <td>
                      <div className="form-check">
                        <input
                          type="checkbox"
                          className="form-check-input"
                          id={`question-${question.id}`}
                          checked={selectedQuestionIds.includes(question.id)}
                          onChange={() => handleCheckboxChange(question.id)}
                        />
                      </div>
                    </td>
                    <td className="text-truncate" style={{ maxWidth: '300px' }}>
                      {question.content}
                    </td>
                    <td>
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
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center p-5">
              <p>No questions found</p>
            </div>
          )}
        </div>
        
        {pagination && pagination.total_pages > 1 && (
          <div className="d-flex justify-content-between align-items-center pt-3">
            <div className="text-muted small">
              Showing {((pagination.current_page - 1) * 10) + 1} to {Math.min(pagination.current_page * 10, pagination.total_items || 0)} of {pagination.total_items || 0} questions
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
                  
                  if (currentPage > 3) {
                    pages.push(1);
                    if (currentPage > 4) {
                      pages.push('...');
                    }
                  }
                  
                  const start = Math.max(1, currentPage - 2);
                  const end = Math.min(totalPages, currentPage + 2);
                  
                  for (let i = start; i <= end; i++) {
                    pages.push(i);
                  }
                  
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
      </Modal.Body>
      <Modal.Footer>
        <div className="d-flex justify-content-between w-100">
          <div>
            <span className="me-2">
              {selectedQuestionIds.length} question(s) selected
            </span>
          </div>
          <div>
            <Button 
              variant="secondary" 
              onClick={onHide} 
              className="me-2"
            >
              Cancel
            </Button>
            <Button 
              variant="primary" 
              onClick={handleAddSelectedQuestions}
              isLoading={isAdding}
              disabled={isAdding || selectedQuestionIds.length === 0}
            >
              Add Selected Questions
            </Button>
          </div>
        </div>
      </Modal.Footer>
    </Modal>
  );
};

export default SelectQuestionsModal;
