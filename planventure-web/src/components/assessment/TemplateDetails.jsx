import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import { Modal } from 'react-bootstrap';
import toast from 'react-hot-toast';

const TemplateDetails = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  const [template, setTemplate] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Clone modal state
  const [showCloneModal, setShowCloneModal] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [isCloning, setIsCloning] = useState(false);
  
  useEffect(() => {
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
      navigate(`/assessments`);
    })
    .catch(error => {
      handleError(error);
    });
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
            <h5 className="mb-0">Questions ({questions.length})</h5>
            <div>
              <Link to="/assessments/questions/create" className="btn btn-sm btn-primary">
                <i className="bi bi-plus-circle me-1"></i> Add New Question
              </Link>
            </div>
          </div>
          
          <div className="card-body p-0">
            {questions.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover mb-0">
                  <thead>
                    <tr>
                      <th>Content</th>
                      <th>Type</th>
                      <th>Options</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {questions.map(question => (
                      <tr key={question.id}>
                        <td className="text-truncate" style={{ maxWidth: '300px' }}>
                          {question.content}
                        </td>
                        <td>
                          <span className={`badge ${getQuestionTypeBadge(question.specialization)}`}>
                            {formatQuestionType(question.specialization)}
                          </span>
                        </td>
                        <td>
                          {question.options ? question.options.length : '-'}
                        </td>
                        <td>
                          <Link 
                            to={`/assessments/questions/${question.id}`}
                            className="btn btn-sm btn-outline-secondary"
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center p-5">
                <p className="mb-3">No questions in this template yet</p>
                <Link to="/assessments/questions" className="btn btn-primary">
                  Add Questions
                </Link>
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
      </div>
    </div>
  );
};

const formatQuestionType = (specialization) => {
  switch (specialization) {
    case 'aptitude':
      return 'Multiple Choice';
    case 'reading_comprehension':
      return 'Reading';
    case 'typing':
      return 'Typing';
    default:
      return specialization;
  }
};

const getQuestionTypeBadge = (specialization) => {
  switch (specialization) {
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
