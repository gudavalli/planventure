import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const AssessmentDashboard = () => {
  const [templates, setTemplates] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);
  const [isLoadingAssessments, setIsLoadingAssessments] = useState(true);
  const [templatesPage, setTemplatesPage] = useState(1);
  const [assessmentsPage, setAssessmentsPage] = useState(1);
  const [templatesPagination, setTemplatesPagination] = useState({});
  const [assessmentsPagination, setAssessmentsPagination] = useState({});
  
  const { handleError } = useApiErrorHandler();

  const loadTemplates = useCallback(async (page = 1) => {
    setIsLoadingTemplates(true);
    try {
      const response = await assessmentService.getTemplates(page);
      setTemplates(response.templates);
      setTemplatesPagination(response.pagination);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingTemplates(false);
    }
  }, [handleError]);

  const loadAssessments = useCallback(async (page = 1) => {
    setIsLoadingAssessments(true);
    try {
      const response = await assessmentService.getAssessments({ 
        page,
        per_page: 10,
        sort_by: 'updated_at',
        order: 'desc'
      });
      setAssessments(response.assessments);
      setAssessmentsPagination(response.pagination);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoadingAssessments(false);
    }
  }, [handleError]);

  useEffect(() => {
    loadTemplates(templatesPage);
    loadAssessments(assessmentsPage);
  }, [loadTemplates, loadAssessments, templatesPage, assessmentsPage]);

  const handleTemplatesPageChange = (newPage) => {
    setTemplatesPage(newPage);
  };

  const handleAssessmentsPageChange = (newPage) => {
    setAssessmentsPage(newPage);
  };
  const createAssessmentForUser = async (templateId) => {
    const email = prompt("Enter candidate's email address:");
    if (!email) return;
    
    try {
      await assessmentService.createAssessment({
        template_id: templateId,
        user_email: email
      });
      toast.success(`Assessment created for ${email}`);
      loadAssessments(1);
    } catch (err) {
      handleError(err);
    }
  };

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Assessment Management</h1>
          <Link to="/assessments/templates/create" className="btn btn-primary">
            <i className="bi bi-plus-circle me-2"></i>Create Template
          </Link>
        </div>
          {/* Templates Section */}
        <div className="card shadow-sm mb-4">
          <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Assessment Templates</h5>            <div>
              <Link to="/question-bank" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>
          </div>
          
          <div className="card-body p-0">
            {isLoadingTemplates ? (
              <div className="d-flex justify-content-center p-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : templates.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover mb-0">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Questions</th>
                      <th>Time Limit</th>
                      <th>Created</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {templates.map(template => (
                      <tr key={template.id}>
                        <td>
                          <Link to={`/assessments/templates/${template.id}`}>
                            {template.name}
                          </Link>
                        </td>
                        <td>{template.question_count}</td>
                        <td>{template.time_limit ? `${template.time_limit} min` : 'No limit'}</td>
                        <td>{new Date(template.created_at).toLocaleDateString()}</td>
                        <td>
                          <Button 
                            variant="outline"
                            size="sm"
                            className="me-2"
                            onClick={() => createAssessmentForUser(template.id)}
                          >
                            <i className="bi bi-send me-1"></i> Send
                          </Button>
                          <Link 
                            to={`/assessments/templates/${template.id}/analytics`}
                            className="btn btn-sm btn-outline-secondary"
                          >
                            <i className="bi bi-graph-up me-1"></i> Analytics
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center p-5">
                <p className="mb-0">No templates found</p>
                <Link to="/assessments/templates/create" className="btn btn-sm btn-primary mt-2">
                  Create your first template
                </Link>
              </div>            )}
            
            {templatesPagination && templatesPagination.total_pages > 1 && (
              <div className="d-flex justify-content-center p-3">
                <nav aria-label="Template pagination">
                  <ul className="pagination mb-0">
                    <li className={`page-item ${!templatesPagination.has_prev ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handleTemplatesPageChange(templatesPagination.page - 1)}
                        disabled={!templatesPagination.has_prev}
                      >
                        Previous
                      </Button>
                    </li>
                    {[...Array(templatesPagination.total_pages).keys()].map(page => (
                      <li key={page + 1} className={`page-item ${templatesPagination.page === page + 1 ? 'active' : ''}`}>
                        <Button 
                          className="page-link" 
                          onClick={() => handleTemplatesPageChange(page + 1)}
                        >
                          {page + 1}
                        </Button>
                      </li>
                    ))}
                    <li className={`page-item ${!templatesPagination.has_next ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handleTemplatesPageChange(templatesPagination.page + 1)}
                        disabled={!templatesPagination.has_next}
                      >
                        Next
                      </Button>
                    </li>
                  </ul>
                </nav>
              </div>
            )}
          </div>
        </div>        {/* Assessments Section */}        <div className="card shadow-sm">
          <div className="card-header bg-white py-3">
            <h5 className="mb-0">Recent Assessments</h5>
          </div>
          
          <div className="card-body p-0">
            {isLoadingAssessments ? (
              <div className="d-flex justify-content-center p-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : assessments.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover mb-0">
                  <thead>
                    <tr>
                      <th>Candidate</th>
                      <th>Template</th>
                      <th>Status</th>
                      <th>Started</th>
                      <th>Completed</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {assessments.map(assessment => (
                      <tr key={assessment.id}>
                        <td>{assessment.user_email}</td>
                        <td>{assessment.template_name}</td>
                        <td>
                          <span className={`badge ${getBadgeColorByStatus(assessment.status)}`}>
                            {formatStatus(assessment.status)}
                          </span>
                        </td>
                        <td>{assessment.start_time ? new Date(assessment.start_time).toLocaleString() : '-'}</td>
                        <td>{assessment.end_time ? new Date(assessment.end_time).toLocaleString() : '-'}</td>
                        <td>
                          {assessment.status === 'completed' && (
                            <Link 
                              to={`/assessments/results/${assessment.id}`}
                              className="btn btn-sm btn-outline-primary"
                            >
                              View Results
                            </Link>
                          )}
                          {assessment.status === 'pending' && (
                            <Button 
                              variant="outline"
                              size="sm"
                              className="me-2"
                              onClick={() => getAssessmentLink(assessment.id)}
                            >
                              Get Link
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center p-5">
                <p className="mb-0">No assessments found</p>
              </div>            )}
            
            {assessmentsPagination && assessmentsPagination.total_pages > 1 && (
              <div className="d-flex justify-content-center p-3">
                <nav aria-label="Assessments pagination">
                  <ul className="pagination mb-0">
                    <li className={`page-item ${!assessmentsPagination.has_prev ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handleAssessmentsPageChange(assessmentsPagination.page - 1)}
                        disabled={!assessmentsPagination.has_prev}
                      >
                        Previous
                      </Button>
                    </li>
                    {[...Array(assessmentsPagination.total_pages).keys()].map(page => (
                      <li key={page + 1} className={`page-item ${assessmentsPagination.page === page + 1 ? 'active' : ''}`}>
                        <Button 
                          className="page-link" 
                          onClick={() => handleAssessmentsPageChange(page + 1)}
                        >
                          {page + 1}
                        </Button>
                      </li>
                    ))}
                    <li className={`page-item ${!assessmentsPagination.has_next ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handleAssessmentsPageChange(assessmentsPagination.page + 1)}
                        disabled={!assessmentsPagination.has_next}
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

// Helper functions
const formatStatus = (status) => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'in_progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    default:
      return status;
  }
};

const getBadgeColorByStatus = (status) => {
  switch (status) {
    case 'pending':
      return 'bg-warning';
    case 'in_progress':
      return 'bg-info';
    case 'completed':
      return 'bg-success';
    default:
      return 'bg-secondary';
  }
};

const getAssessmentLink = async (assessmentId) => {
  try {
    const response = await assessmentService.getAssessmentDetails(assessmentId);
    if (response.access_url) {
      // Create full URL
      const baseUrl = window.location.origin;
      const fullUrl = `${baseUrl}${response.access_url}`;
      
      // Copy to clipboard
      navigator.clipboard.writeText(fullUrl)
        .then(() => {
          toast.success('Assessment link copied to clipboard');
        })
        .catch(err => {
          console.error('Could not copy text: ', err);
          // Fall back to prompting the user to copy manually
          prompt('Copy this assessment link:', fullUrl);
        });
    }  } catch (error) {
    console.error('Failed to get assessment link:', error);
    toast.error('Failed to get assessment link');
  }
};

export default AssessmentDashboard;
