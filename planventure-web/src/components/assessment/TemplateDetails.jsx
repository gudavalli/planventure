import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import { Modal } from 'react-bootstrap';
import toast from 'react-hot-toast';
import SelectQuestionsModal from './SelectQuestionsModal';

const TemplateDetails = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  const [template, setTemplate] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  
  // Modal states
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [showAddQuestionsModal, setShowAddQuestionsModal] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [isCloning, setIsCloning] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [questionToDelete, setQuestionToDelete] = useState(null);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  
  // Calculate pagination
  const totalQuestions = questions.length;
  const totalPages = Math.ceil(totalQuestions / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentQuestions = questions.slice(startIndex, endIndex);
  
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };
  
  useEffect(() => {
    const fetchTemplateDetails = async () => {
      try {
        const templateData = await assessmentService.getTemplateDetails(templateId);
        setTemplate(templateData);
        
        // If template has questions, fetch them
        if (templateData.questions) {
          setQuestions(templateData.questions);
        }
        
        // Reset to first page when template changes
        setCurrentPage(1);
      } catch (error) {
        handleError(error);
        navigate('/assessments');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchTemplateDetails();
  }, [templateId, navigate, handleError]);
  
  // Handle clone template modal
  const openCloneModal = () => {
    if (template) {
      setNewTemplateName(`${template.name} (Copy)`);
      setShowCloneModal(true);
    }
  };
  
  const handleCloneTemplate = async () => {
    if (!newTemplateName.trim()) {
      toast.error('Template name cannot be empty');
      return;
    }
    
    setIsCloning(true);
    try {
      const clonedTemplate = await assessmentService.cloneTemplate(templateId, newTemplateName);
      toast.success('Template cloned successfully!');
      setShowCloneModal(false);
      // Navigate to the new template
      navigate(`/assessments/templates/${clonedTemplate.id}`);
    } catch (error) {
      handleError(error);
    } finally {
      setIsCloning(false);
    }
  };
  
  const createAssessmentForUser = () => {
    const email = prompt("Enter candidate's email address:");
    if (!email) return;
    
    assessmentService.createAssessment({
      template_id: templateId,
      user_email: email
    })
    .then(() => {
      toast.success(`Assessment created for ${email}`);
      // Stay on the current template details page instead of navigating away
    })
    .catch(error => {
      handleError(error);
    });
  };
  
  const openDeleteConfirmation = (question) => {
    setQuestionToDelete(question);
    setShowDeleteConfirmation(true);
  };
  
  const handleDeleteQuestion = async () => {
    if (!questionToDelete) return;
    
    setIsDeleting(true);
    try {
      await assessmentService.removeQuestionFromTemplate(templateId, questionToDelete.id);
      toast.success('Question removed from template successfully');
      
      // Refresh template details
      const templateData = await assessmentService.getTemplateDetails(templateId);
      setTemplate(templateData);
      
      if (templateData.questions) {
        setQuestions(templateData.questions);
      }
      
      setShowDeleteConfirmation(false);
      setQuestionToDelete(null);
    } catch (error) {
      handleError(error);
    } finally {
      setIsDeleting(false);
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
  
  if (!template) return null;
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 className="h3 mb-1">{template.name}</h1>
            <p className="text-muted mb-0">
              {template.time_limit ? `${template.time_limit} min` : 'No time limit'} | 
              {template.percentage}% of questions | 
              Created {new Date(template.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="d-flex">
            <Button
              variant="outline-primary"
              className="me-2"
              onClick={createAssessmentForUser}
            >
              <i className="bi bi-envelope me-1"></i> Send Assessment
            </Button>
            
            <Link
              to={`/assessments/templates/${templateId}/analytics`}
              className="btn btn-outline-secondary me-2"
            >
              <i className="bi bi-graph-up me-1"></i> Analytics
            </Link>
            
            <Button
              variant="outline-success"
              onClick={openCloneModal}
            >
              <i className="bi bi-files me-1"></i> Clone
            </Button>
          </div>
        </div>
        
        {template.description && (
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h5>Description</h5>
              <p className="mb-0">{template.description}</p>
            </div>
          </div>
        )}
        
        {/* Questions Section */}
        <div className="card shadow-sm mb-4">
          <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Questions ({totalQuestions})</h5>
            <div>
              <Button 
                variant="primary"
                className="btn-sm me-2"
                onClick={() => setShowAddQuestionsModal(true)}
              >
                <i className="bi bi-plus-circle me-1"></i> Add Questions
              </Button>              <Link to="/question-bank/create" className="btn btn-sm btn-outline-primary">
                <i className="bi bi-plus-circle me-1"></i> Create New Question
              </Link>
            </div>
          </div>
          
          <div className="card-body p-0">
            {totalQuestions > 0 ? (
              <>
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Content</th>
                        <th>Type</th>
                        <th>Subject</th>
                        <th>Options</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {currentQuestions.map(question => (
                        <tr key={question.id}>
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
                          <td>                            <div className="btn-group" role="group">
                              <Link 
                                to={`/question-bank/${question.id}`}
                                state={{ from: `/assessments/templates/${templateId}` }}
                                className="btn btn-sm btn-outline-secondary"
                              >
                                View
                              </Link>
                              <Link 
                                to={`/question-bank/${question.id}/edit?returnTo=${encodeURIComponent(`/assessments/templates/${templateId}`)}`}
                                className="btn btn-sm btn-outline-primary"
                              >
                                Edit
                              </Link>
                              <Button 
                                variant="outline-danger"
                                className="btn-sm"
                                onClick={() => openDeleteConfirmation(question)}
                              >
                                <i className="bi bi-trash"></i>
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="d-flex justify-content-between align-items-center p-3">
                    <div className="text-muted small">
                      Showing {startIndex + 1} to {Math.min(endIndex, totalQuestions)} of {totalQuestions} questions
                    </div>
                    <nav aria-label="Template questions pagination">
                      <ul className="pagination mb-0">
                        <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                          <Button 
                            className="page-link" 
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                          >
                            Previous
                          </Button>
                        </li>
                        {(() => {
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
                        <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                          <Button 
                            className="page-link" 
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
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
                <p className="mb-3">No questions in this template yet</p>
                <Button 
                  variant="primary"
                  onClick={() => setShowAddQuestionsModal(true)}
                >
                  Add Questions
                </Button>
              </div>
            )}
          </div>
        </div>
      
        {/* Clone Template Modal */}
        <Modal show={showCloneModal} onHide={() => setShowCloneModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Clone Assessment Template</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <form onSubmit={(e) => { e.preventDefault(); handleCloneTemplate(); }}>
              <div className="mb-3">
                <label htmlFor="templateName" className="form-label">Template Name</label>
                <Input
                  id="templateName"
                  type="text"
                  value={newTemplateName}
                  onChange={(e) => setNewTemplateName(e.target.value)}
                  placeholder="Enter a name for the cloned template"
                  required
                />
              </div>
            </form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCloneModal(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleCloneTemplate}
              isLoading={isCloning}
              disabled={isCloning || !newTemplateName.trim()}
            >
              Clone Template
            </Button>
          </Modal.Footer>
        </Modal>

        {/* Add Questions Modal */}
        <SelectQuestionsModal
          show={showAddQuestionsModal}
          onHide={() => setShowAddQuestionsModal(false)}
          templateId={templateId}
          onQuestionsAdded={() => {
            // Refresh template details after adding questions
            const fetchTemplateDetails = async () => {
              try {
                const templateData = await assessmentService.getTemplateDetails(templateId);
                setTemplate(templateData);
                
                // If template has questions, fetch them
                if (templateData.questions) {
                  setQuestions(templateData.questions);
                }
              } catch (error) {
                handleError(error);
              }
            };
            
            fetchTemplateDetails();
          }}
        />

        {/* Delete Question Confirmation Modal */}
        <Modal show={showDeleteConfirmation} onHide={() => setShowDeleteConfirmation(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Confirm Removal</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {questionToDelete && (
              <div>
                <p>Are you sure you want to remove this question from the template?</p>
                <div className="alert alert-secondary">
                  <strong>Question:</strong> {questionToDelete.content.length > 100 
                    ? `${questionToDelete.content.substring(0, 100)}...` 
                    : questionToDelete.content}
                </div>
                <p className="text-muted mb-0">
                  <small>Note: This will only remove the question from this template. The question itself will not be deleted.</small>
                </p>
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowDeleteConfirmation(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteQuestion}
              isLoading={isDeleting}
              disabled={isDeleting}
            >
              Remove Question
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    </div>
  );
};

// Helper function to determine the actual question type based on question structure
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

// Helper function to get the subject specialization
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

export default TemplateDetails;
