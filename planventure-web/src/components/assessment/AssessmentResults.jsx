import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Navigation from '../Navigation';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import { useAuth } from '../../context/auth-hooks';
import PDFExport from './PDFExport';
import toast from 'react-hot-toast';

const AssessmentResults = () => {
  const { assessmentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  const { user } = useAuth();
  
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Parse query parameters for public access
  const queryParams = new URLSearchParams(location.search);
  const email = queryParams.get('email');
  const token = queryParams.get('token');
  const isPublicAccess = email && token;
  
  useEffect(() => {
    const fetchReport = async () => {
      try {
        // For authenticated users (admin, talent lead)
        if (user && (user.role === 'admin' || user.role === 'talent_lead')) {
          const reportData = await assessmentService.getAssessmentReport(assessmentId);
          setReport(reportData);
        }
        // For public access (candidate)
        else if (isPublicAccess) {
          // First verify access
          await assessmentService.accessAssessment(assessmentId, email, token);
          
          // Then get report
          const reportData = await assessmentService.getAssessmentReport(assessmentId);
          setReport(reportData);
        } 
        // No valid access method
        else {
          toast.error('Unauthorized access');
          navigate('/');
        }
      } catch (error) {
        handleError(error);
        if (isPublicAccess) {
          navigate('/');
        } else {
          navigate('/assessments');
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchReport();
  }, [assessmentId, email, token, user, navigate, handleError, isPublicAccess]);
  
  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  if (!report) return null;
    return (
    <div className="min-vh-100 bg-light">
      {!isPublicAccess && <Navigation />}
      
      <div className="container py-4">
        <PDFExport filename={`assessment-result-${report.user_email.replace('@', '-at-')}.pdf`}>
          <div className="card shadow-sm mb-4">
            <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Assessment Results</h5>
              <div className="d-print-none">
                <button 
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => window.print()}
                >
                  <i className="bi bi-printer me-1"></i> Print
                </button>
              </div>
            </div>
            
            <div className="card-body p-4">
            <div className="row mb-4">
              <div className="col-md-6">
                <h2 className="h4">
                  {report.template_name}
                </h2>
                <p className="text-muted">
                  Candidate: {report.user_email}
                </p>
              </div>
              
              <div className="col-md-6 text-md-end">
                <h3 className="h4 mb-0">
                  Overall Score: <span className={`badge ${getScoreBadgeColor(report.overall_score)}`}>
                    {report.overall_score}%
                  </span>
                </h3>
                <p className="text-muted">
                  {formatDuration(report.time_taken)}
                </p>
              </div>
            </div>
            
            {/* Section scores */}
            <h5 className="mb-3">Section Scores</h5>
            <div className="row mb-4">
              {Object.entries(report.section_scores).map(([section, data]) => (
                <div className="col-md-4 mb-3" key={section}>
                  <div className="card h-100">
                    <div className="card-body">
                      <h6 className="card-title">{formatSection(section)}</h6>
                      <div className="d-flex align-items-center">
                        <div className="me-3">
                          <span className={`badge ${getScoreBadgeColor(data.score)}`}>
                            {Math.round(data.score)}%
                          </span>
                        </div>
                        <div>
                          <small className="text-muted">
                            {data.correct}/{data.questions} correct
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Question details */}
            <h5 className="mb-3">Question Details</h5>
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th style={{width: '60%'}}>Question</th>
                    <th>Type</th>
                    <th>Your Answer</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {report.question_details.map((question, index) => (
                    <tr key={question.id}>
                      <td>
                        <div className="fw-medium">{question.content}</div>
                        {question.specialization === 'aptitude' && (
                          <div className="small text-muted mt-1">
                            <span className="fw-bold">Correct Answer:</span> {question.correct_answer}
                          </div>
                        )}
                      </td>
                      <td>{formatSection(question.specialization)}</td>
                      <td>
                        {question.specialization === 'typing' ? (
                          <span className="badge bg-info">Typing Test</span>
                        ) : (
                          <span>{question.user_answer}</span>
                        )}
                      </td>
                      <td>
                        {question.specialization === 'typing' ? (
                          <span className={`badge ${getScoreBadgeColor(question.score * 100)}`}>
                            {Math.round(question.score * 100)}%
                          </span>
                        ) : (
                          <span className={question.is_correct ? "text-success" : "text-danger"}>
                            {question.is_correct ? 
                              <i className="bi bi-check-circle-fill"></i> : 
                              <i className="bi bi-x-circle-fill"></i>
                            }
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="mt-4 text-center">
              <p className="text-muted small">
                Assessment completed on {new Date(report.end_time).toLocaleString()}
              </p>            </div>
          </div>
        </div>
        </PDFExport>
      </div>
    </div>
  );
};

// Helper functions
const formatDuration = (seconds) => {
  if (!seconds) return 'No time data';
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  
  if (minutes < 1) {
    return `${remainingSeconds} seconds`;
  } else if (minutes === 1) {
    return `${minutes} minute ${remainingSeconds} seconds`;
  } else {
    return `${minutes} minutes ${remainingSeconds} seconds`;
  }
};

const formatSection = (section) => {
  switch (section) {
    case 'aptitude':
      return 'Technical Knowledge';
    case 'reading_comprehension':
      return 'Reading Comprehension';
    case 'typing':
      return 'Typing Test';
    default:
      return section.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
};

const getScoreBadgeColor = (score) => {
  if (score >= 80) return 'bg-success';
  if (score >= 60) return 'bg-primary';
  if (score >= 40) return 'bg-warning';
  return 'bg-danger';
};

export default AssessmentResults;
