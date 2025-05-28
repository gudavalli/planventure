import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import Navigation from '../Navigation';
import Button from '../Button';
import { Modal } from 'react-bootstrap';
import toast from 'react-hot-toast';

const QuestionBankDashboard = () => {
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');  const [selectedSpecialization, setSelectedSpecialization] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [selectedQuestionType, setSelectedQuestionType] = useState('');  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    totalItems: 0,
    limit: 10
  });
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [questionToDelete, setQuestionToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const { handleError } = useApiErrorHandler();
  const specializations = [
    { value: '', label: 'All Specializations' },
    { value: 'aptitude', label: 'Aptitude' },
    { value: 'verbal', label: 'Verbal' },
    { value: 'quantitative', label: 'Quantitative' },
    { value: 'logical', label: 'Logical' },
    { value: 'technical', label: 'Technical' },
    { value: 'programming', label: 'Programming' },
    { value: 'analytics', label: 'Analytics' },
    { value: 'typing', label: 'Typing' },
    { value: 'reading_comprehension', label: 'Reading Comprehension' }
  ];
  const difficulties = [
    { value: '', label: 'All Difficulties' },
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];
const fetchQuestions = useCallback(async () => {
    setIsLoading(true);
    try {
      // Use the correct API call format: (page, perPage, type, search, specialization, difficulty)
      const response = await assessmentService.getQuestions(
        pagination.page, 
        pagination.limit, 
        selectedQuestionType || 'all', 
        searchTerm || '',
        selectedSpecialization || '',
        selectedDifficulty || ''
      );
      
      // Handle the response format with pagination data
      if (response && typeof response === 'object' && response.questions) {
        setQuestions(response.questions);
        setPagination(prev => ({
          ...prev,
          totalPages: response.pagination?.total_pages || 1,
          totalItems: response.pagination?.total_items || 0,
          currentPage: response.pagination?.current_page || pagination.page,
          hasNext: response.pagination?.has_next || false,
          hasPrev: response.pagination?.has_prev || false
        }));
      } else if (Array.isArray(response)) {
        // Fallback for direct array response
        setQuestions(response);
        setPagination(prev => ({
          ...prev,
          totalPages: 1,
          totalItems: response.length,
          currentPage: 1,
          hasNext: false,
          hasPrev: false
        }));
      } else {
        setQuestions([]);
        setPagination(prev => ({
          ...prev,
          totalPages: 1,
          totalItems: 0,
          currentPage: 1,
          hasNext: false,
          hasPrev: false
        }));
      }
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.page, pagination.limit, searchTerm, selectedQuestionType, selectedSpecialization, selectedDifficulty, handleError]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleDelete = async () => {
    if (!questionToDelete) return;
    
    setIsDeleting(true);
    try {
      await assessmentService.deleteQuestion(questionToDelete.id);
      toast.success('Question deleted successfully');
      setQuestions(questions.filter(q => q.id !== questionToDelete.id));
      setDeleteModalOpen(false);
      setQuestionToDelete(null);
      
      // Refresh the list to get updated pagination
      fetchQuestions();
    } catch (error) {
      handleError(error);
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteModal = (question) => {
    setQuestionToDelete(question);
    setDeleteModalOpen(true);
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

  const getQuestionTypeBadgeClass = (question) => {
    const questionType = getQuestionType(question);
    switch (questionType) {
      case 'aptitude':
        return 'badge bg-primary';
      case 'reading_comprehension':
        return 'badge bg-info';
      case 'typing':
        return 'badge bg-success';
      default:
        return 'badge bg-secondary';
    }
  };

  const formatQuestionType = (question) => {
    const questionType = getQuestionType(question);
    switch (questionType) {
      case 'aptitude':
        return 'Multiple Choice';
      case 'reading_comprehension':
        return 'Reading Comprehension';
      case 'typing':
        return 'Typing Test';
      default:
        return questionType || 'N/A';
    }
  };

  // Helper function to check filter compatibility
  const getFilterCompatibilityMessage = () => {
    if (selectedQuestionType && selectedSpecialization) {
      // Check for incompatible combinations
      if (selectedQuestionType === 'typing' && selectedSpecialization !== 'typing') {
        return 'Note: Typing questions are typically only found in the "typing" specialization.';
      }
      if (selectedQuestionType === 'reading_comprehension' && selectedSpecialization !== 'reading_comprehension') {
        return 'Note: Reading comprehension questions are typically only found in the "reading_comprehension" specialization.';
      }
      if (selectedQuestionType === 'aptitude' && ['typing', 'reading_comprehension'].includes(selectedSpecialization)) {
        return 'Note: Aptitude (multiple choice) questions are typically not found in typing or reading comprehension specializations.';
      }
    }
    return null;
  };

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      <div className="container-fluid py-4">
        <div className="row">
          <div className="col-12">
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h1 className="h3 mb-0">Question Bank</h1>
                <p className="text-muted">Manage your assessment questions independently</p>
              </div>
              <Link to="/question-bank/create" className="btn btn-primary">
                <i className="bi bi-plus-circle me-2"></i>
                Create Question
              </Link>
            </div>            {/* Filters */}
            <div className="card mb-4">
              <div className="card-body">
                <form onSubmit={handleSearch} className="row g-3">
                  <div className="col-md-3">
                    <label htmlFor="search" className="form-label">Search Questions</label>
                    <input
                      type="text"
                      className="form-control"
                      id="search"
                      placeholder="Search by content..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>                  <div className="col-md-2">
                    <label htmlFor="specialization" className="form-label">Specialization</label>
                    <select
                      className="form-select"
                      id="specialization"
                      value={selectedSpecialization}
                      onChange={(e) => {
                        setSelectedSpecialization(e.target.value);
                        setPagination(prev => ({ ...prev, page: 1 }));
                      }}
                    >
                      {specializations.map(spec => (
                        <option key={spec.value} value={spec.value}>
                          {spec.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label htmlFor="difficulty" className="form-label">Difficulty</label>
                    <select
                      className="form-select"
                      id="difficulty"
                      value={selectedDifficulty}
                      onChange={(e) => {
                        setSelectedDifficulty(e.target.value);
                        setPagination(prev => ({ ...prev, page: 1 }));
                      }}
                    >
                      {difficulties.map(diff => (
                        <option key={diff.value} value={diff.value}>
                          {diff.label}
                        </option>
                      ))}
                    </select>
                  </div>                  <div className="col-md-3">
                    <label htmlFor="questionType" className="form-label">Question Type</label>
                    <select
                      className="form-select"
                      id="questionType"
                      value={selectedQuestionType}
                      onChange={(e) => {
                        setSelectedQuestionType(e.target.value);
                        setPagination(prev => ({ ...prev, page: 1 }));
                      }}
                    >
                      <option value="">All Types</option>
                      <option value="aptitude">Multiple Choice</option>
                      <option value="reading_comprehension">Reading Comprehension</option>
                      <option value="typing">Typing Test</option>
                    </select>
                  </div>
                  <div className="col-md-2">
                    <label className="form-label">&nbsp;</label>
                    <div className="d-grid">
                      <Button type="submit" variant="outline-primary">
                        <i className="bi bi-search me-1"></i>
                        Filter
                      </Button>
                    </div>
                  </div>                </form>
                
                {/* Filter compatibility message */}
                {getFilterCompatibilityMessage() && (
                  <div className="mt-3">
                    <div className="alert alert-warning alert-dismissible fade show" role="alert">
                      <i className="bi bi-info-circle me-2"></i>
                      {getFilterCompatibilityMessage()}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Statistics */}
            <div className="row mb-4">
              <div className="col-md-3">
                <div className="card bg-primary text-white">
                  <div className="card-body">
                    <div className="d-flex justify-content-between">
                      <div>
                        <h5 className="card-title">Total Questions</h5>
                        <h3 className="mb-0">{pagination.totalItems}</h3>
                      </div>
                      <div className="align-self-center">
                        <i className="bi bi-question-circle-fill fs-1"></i>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Questions List */}
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Questions ({pagination.totalItems})</h5>
              </div>
              <div className="card-body">
                {isLoading ? (
                  <div className="text-center py-4">
                    <div className="spinner-border" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                  </div>
                ) : questions.length === 0 ? (
                  <div className="text-center py-5">
                    <i className="bi bi-question-circle fs-1 text-muted mb-3"></i>
                    <h5 className="text-muted">No questions found</h5>                    <p className="text-muted">
                      {searchTerm || selectedSpecialization || selectedDifficulty || selectedQuestionType
                        ? 'Try adjusting your filters'
                        : 'Create your first question to get started'
                      }
                    </p>
                    <Link to="/question-bank/create" className="btn btn-primary">
                      Create Question
                    </Link>
                  </div>
                ) : (
                  <>
                    <div className="table-responsive">                      <table className="table table-hover">
                        <thead>
                          <tr>
                            <th>Question</th>
                            <th>Type</th>
                            <th>Specialization</th>
                            <th>Difficulty</th>
                            <th>Time Limit</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {questions.map((question) => (
                            <tr key={question.id}>
                              <td>
                                <div className="question-content">
                                  <p className="mb-1 fw-semibold">
                                    {question.content?.length > 100
                                      ? `${question.content.substring(0, 100)}...`
                                      : question.content
                                    }
                                  </p>
                                  {question.options && question.options.length > 0 && (
                                    <small className="text-muted">
                                      Multiple choice ({question.options.length} options)
                                    </small>
                                  )}
                                </div>
                              </td>                              <td>
                                <span className={getQuestionTypeBadgeClass(question)}>
                                  {formatQuestionType(question)}
                                </span>
                              </td>
                              <td>
                                <span className={getSpecializationBadgeClass(question.specialization)}>
                                  {question.specialization || 'N/A'}
                                </span>
                              </td>
                              <td>
                                <span className={getDifficultyBadgeClass(question.difficulty)}>
                                  {question.difficulty || 'N/A'}
                                </span>
                              </td>
                              <td>
                                {question.time_limit ? `${question.time_limit}s` : 'N/A'}
                              </td>
                              <td>
                                <div className="btn-group btn-group-sm">
                                  <Link
                                    to={`/question-bank/${question.id}`}
                                    className="btn btn-outline-primary"
                                    title="View Question"
                                  >
                                    <i className="bi bi-eye"></i>
                                  </Link>
                                  <Link
                                    to={`/question-bank/${question.id}/edit`}
                                    className="btn btn-outline-secondary"
                                    title="Edit Question"
                                  >
                                    <i className="bi bi-pencil"></i>
                                  </Link>
                                  <button
                                    type="button"
                                    className="btn btn-outline-danger"
                                    onClick={() => openDeleteModal(question)}
                                    title="Delete Question"
                                  >
                                    <i className="bi bi-trash"></i>
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>                    {/* Pagination - consistent with working components */}
                    {pagination.totalPages > 1 && (
                      <div className="d-flex justify-content-between align-items-center p-3">
                        <div className="text-muted small">
                          Showing {((pagination.currentPage - 1) * pagination.limit) + 1} to {Math.min(pagination.currentPage * pagination.limit, pagination.totalItems)} of {pagination.totalItems} questions
                        </div>
                        <nav aria-label="Question pagination">
                          <ul className="pagination mb-0">
                            <li className={`page-item ${!pagination.hasPrev ? 'disabled' : ''}`}>
                              <button
                                className="page-link"
                                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                                disabled={!pagination.hasPrev}
                              >
                                Previous
                              </button>
                            </li>
                            {(() => {
                              const currentPage = pagination.currentPage;
                              const totalPages = pagination.totalPages;
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
                                    <button
                                      className="page-link"
                                      onClick={() => setPagination(prev => ({ ...prev, page: pageNum }))}
                                    >
                                      {pageNum}
                                    </button>
                                  </li>
                                );
                              });
                            })()}
                            <li className={`page-item ${!pagination.hasNext ? 'disabled' : ''}`}>
                              <button
                                className="page-link"
                                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                                disabled={!pagination.hasNext}
                              >
                                Next
                              </button>
                            </li>
                          </ul>
                        </nav>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>      {/* Delete Confirmation Modal */}
      <Modal
        show={deleteModalOpen}
        onHide={() => {
          setDeleteModalOpen(false);
          setQuestionToDelete(null);
        }}
      >
        <Modal.Header closeButton>
          <Modal.Title>Confirm Deletion</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete this question?</p>
          {questionToDelete && (
            <div className="bg-light p-3 rounded">
              <strong>Question:</strong> {questionToDelete.content}
            </div>
          )}
          <p className="text-danger mt-3 mb-0">
            <i className="bi bi-exclamation-triangle me-2"></i>
            This action cannot be undone.
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={() => {
              setDeleteModalOpen(false);
              setQuestionToDelete(null);
            }}
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

export default QuestionBankDashboard;
