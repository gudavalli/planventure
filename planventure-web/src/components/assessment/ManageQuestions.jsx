import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const ManageQuestions = () => {
  const { handleError } = useApiErrorHandler();
  
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  
  useEffect(() => {
    fetchQuestions();
  }, [page, filter]);
  
  const fetchQuestions = async () => {
    setIsLoading(true);
    try {
      // Assuming there's an API endpoint for questions
      const response = await assessmentService.getQuestions(page, 10, filter, search);
      setQuestions(response.questions);
      setPagination(response.pagination);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };
  
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
              
              <div className="col-md-6 col-lg-3 ms-auto">
                <select
                  className="form-select"
                  value={filter}
                  onChange={handleFilterChange}
                >
                  <option value="all">All Types</option>
                  <option value="aptitude">Multiple Choice</option>
                  <option value="reading_comprehension">Reading Comprehension</option>
                  <option value="typing">Typing</option>
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
                <table className="table table-hover mb-0">
                  <thead>
                    <tr>
                      <th style={{ width: '50%' }}>Content</th>
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
            )}
            
            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="d-flex justify-content-center p-3">
                <nav aria-label="Question pagination">
                  <ul className="pagination mb-0">
                    <li className={`page-item ${!pagination.has_prev ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handlePageChange(pagination.page - 1)}
                        disabled={!pagination.has_prev}
                      >
                        Previous
                      </Button>
                    </li>
                    {[...Array(pagination.total_pages).keys()].map(pageNum => (
                      <li key={pageNum + 1} className={`page-item ${pagination.page === pageNum + 1 ? 'active' : ''}`}>
                        <Button 
                          className="page-link" 
                          onClick={() => handlePageChange(pageNum + 1)}
                        >
                          {pageNum + 1}
                        </Button>
                      </li>
                    ))}
                    <li className={`page-item ${!pagination.has_next ? 'disabled' : ''}`}>
                      <Button 
                        className="page-link" 
                        onClick={() => handlePageChange(pagination.page + 1)}
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

export default ManageQuestions;
