import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const TemplateAnalytics = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [template, setTemplate] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch template details and analytics in parallel
        const [templateData, analyticsData] = await Promise.all([
          assessmentService.getTemplateDetails(templateId),
          assessmentService.getTemplateAnalytics(templateId)
        ]);
        
        setTemplate(templateData);
        setAnalytics(analyticsData);
      } catch (error) {
        handleError(error);
        navigate('/assessments');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [templateId, navigate, handleError]);
  
  // Prepare chart data
  const getCompletionRateData = () => {
    return {
      labels: ['Completed', 'In Progress', 'Not Started'],
      datasets: [
        {
          data: [
            analytics?.completion_rates?.completed || 0,
            analytics?.completion_rates?.in_progress || 0,
            analytics?.completion_rates?.not_started || 0
          ],
          backgroundColor: [
            'rgba(75, 192, 192, 0.6)', // Teal for completed
            'rgba(255, 206, 86, 0.6)', // Yellow for in progress
            'rgba(201, 203, 207, 0.6)' // Grey for not started
          ],
          borderColor: [
            'rgb(75, 192, 192)',
            'rgb(255, 206, 86)',
            'rgb(201, 203, 207)'
          ],
          borderWidth: 1,
        },
      ],
    };
  };

  const getScoreDistributionData = () => {
    const scoreRanges = analytics?.score_distribution || {};
    return {
      labels: Object.keys(scoreRanges).map(range => `${range}%`),
      datasets: [
        {
          label: 'Candidates',
          data: Object.values(scoreRanges),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgb(54, 162, 235)',
          borderWidth: 1,
        },
      ],
    };
  };
  
  const getPerformanceByQuestionTypeData = () => {
    const questionTypePerf = analytics?.performance_by_question_type || {};
    return {
      labels: Object.keys(questionTypePerf).map(formatQuestionType),
      datasets: [
        {
          label: 'Average Score (%)',
          data: Object.values(questionTypePerf),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',  // Red for multiple choice
            'rgba(54, 162, 235, 0.6)',  // Blue for reading
            'rgba(75, 192, 192, 0.6)'   // Teal for typing
          ],
          borderColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(75, 192, 192)'
          ],
          borderWidth: 1,
        },
      ],
    };
  };
  
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container py-4">
          <div className="d-flex justify-content-center align-items-center" style={{height: '70vh'}}>
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!template || !analytics) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container py-4">
          <div className="alert alert-danger">
            Failed to load analytics data
          </div>
          <Link to="/assessments" className="btn btn-primary">
            Go Back to Assessments
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
          <div>
            <Link to={`/assessments/templates/${templateId}`} className="text-decoration-none">
              <i className="bi bi-chevron-left"></i> Back to Template
            </Link>
            <h1 className="h3 mb-1">Analytics: {template.name}</h1>
            <p className="text-muted">
              {analytics.total_assessments} assessments created | 
              {analytics.unique_candidates} unique candidates
            </p>
          </div>
          
          <Button
            variant="outline-primary"
            onClick={() => window.print()}
          >
            <i className="bi bi-printer me-1"></i> Print Report
          </Button>
        </div>
        
        <div className="row">
          {/* Key metrics */}
          <div className="col-12 mb-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title mb-3">Key Metrics</h5>
                <div className="row g-4 text-center">
                  <div className="col-md-3 col-6">
                    <div className="border rounded p-3">
                      <h6 className="text-muted mb-1">Average Score</h6>
                      <h2 className="mb-0">{analytics.average_score}%</h2>
                    </div>
                  </div>
                  <div className="col-md-3 col-6">
                    <div className="border rounded p-3">
                      <h6 className="text-muted mb-1">Completion Rate</h6>
                      <h2 className="mb-0">{analytics.completion_percentage}%</h2>
                    </div>
                  </div>
                  <div className="col-md-3 col-6">
                    <div className="border rounded p-3">
                      <h6 className="text-muted mb-1">Pass Rate</h6>
                      <h2 className="mb-0">{analytics.pass_rate}%</h2>
                    </div>
                  </div>
                  <div className="col-md-3 col-6">
                    <div className="border rounded p-3">
                      <h6 className="text-muted mb-1">Avg. Time</h6>
                      <h2 className="mb-0">{analytics.average_completion_time} min</h2>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Pie and bar charts */}
          <div className="col-md-6 mb-4">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">Completion Status</h5>
                <div className="d-flex justify-content-center" style={{height: '300px'}}>
                  {analytics.total_assessments > 0 ? (
                    <Pie data={getCompletionRateData()} />
                  ) : (
                    <div className="d-flex align-items-center justify-content-center h-100">
                      <p className="text-muted">No assessment data available</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-md-6 mb-4">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">Score Distribution</h5>
                <div style={{height: '300px'}}>
                  {analytics.total_assessments > 0 ? (
                    <Bar 
                      data={getScoreDistributionData()} 
                      options={barOptions}
                    />
                  ) : (
                    <div className="d-flex align-items-center justify-content-center h-100">
                      <p className="text-muted">No assessment data available</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Question performance */}
          <div className="col-12 mb-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title">Performance by Question Type</h5>
                <div style={{height: '300px'}}>
                  {analytics.total_assessments > 0 && Object.keys(analytics.performance_by_question_type || {}).length > 0 ? (
                    <Bar 
                      data={getPerformanceByQuestionTypeData()} 
                      options={barOptions}
                    />
                  ) : (
                    <div className="d-flex align-items-center justify-content-center h-100">
                      <p className="text-muted">No question performance data available</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Top performers table */}
          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body">
                <h5 className="card-title">Top Performers</h5>
                {analytics.top_performers && analytics.top_performers.length > 0 ? (
                  <div className="table-responsive">
                    <table className="table table-hover">
                      <thead>
                        <tr>
                          <th>Candidate</th>
                          <th>Score</th>
                          <th>Time Taken</th>
                          <th>Date Completed</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.top_performers.map((performer, index) => (
                          <tr key={index}>
                            <td>{performer.candidate_email}</td>
                            <td>
                              <span className="badge bg-success">{performer.score}%</span>
                            </td>
                            <td>{performer.time_taken} min</td>
                            <td>{new Date(performer.completed_at).toLocaleDateString()}</td>
                            <td>
                              <Link 
                                to={`/assessments/results/${performer.assessment_id}`}
                                className="btn btn-sm btn-outline-primary"
                              >
                                View Details
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-muted">No completed assessments yet</p>
                )}
              </div>
            </div>
          </div>
        </div>
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

export default TemplateAnalytics;
