import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import toast from 'react-hot-toast';

const QuestionBankEditQuestion = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [question, setQuestion] = useState(null);
  const [formData, setFormData] = useState({
    content: '',
    specialization: '',
    options: [],
    correct_answer: '',
    explanation: '',
    difficulty: 'medium',
    time_limit: 60
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  const specializations = [
    { value: 'aptitude', label: 'Aptitude' },
    { value: 'verbal', label: 'Verbal' },
    { value: 'quantitative', label: 'Quantitative' },
    { value: 'logical', label: 'Logical' },
    { value: 'technical', label: 'Technical' }
  ];

  const difficulties = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }  ];

  const fetchQuestion = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await assessmentService.getQuestionDetails(questionId);
      setQuestion(data);
      
      // Prepare form data
      const isMultipleChoice = Array.isArray(data.options) && data.options.length > 0;
      let specialization = data.specialization || '';
      if (isMultipleChoice && specialization !== 'aptitude') {
        specialization = 'aptitude';
      }

      setFormData({
        content: data.content || '',
        specialization: specialization,
        options: isMultipleChoice ? data.options : ['', '', '', ''],
        correct_answer: data.correct_answer || '',
        explanation: data.explanation || '',
        difficulty: data.difficulty || 'medium',
        time_limit: data.time_limit || 60
      });
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [questionId, handleError]);

  useEffect(() => {
    fetchQuestion();
  }, [fetchQuestion]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.content.trim()) {
      newErrors.content = 'Question content is required';
    }

    if (!formData.specialization) {
      newErrors.specialization = 'Specialization is required';
    }

    // Validate options if any are filled
    const filledOptions = formData.options.filter(option => option.trim());
    if (filledOptions.length > 0) {
      if (filledOptions.length < 2) {
        newErrors.options = 'Please provide at least 2 options for multiple choice questions';
      }
      
      if (!formData.correct_answer.trim()) {
        newErrors.correct_answer = 'Correct answer is required for multiple choice questions';
      } else if (!filledOptions.includes(formData.correct_answer.trim())) {
        newErrors.correct_answer = 'Correct answer must match one of the provided options';
      }
    }

    if (formData.time_limit && (formData.time_limit < 10 || formData.time_limit > 3600)) {
      newErrors.time_limit = 'Time limit must be between 10 and 3600 seconds';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const filledOptions = formData.options.filter(option => option.trim());
      
      const questionData = {
        ...formData,
        options: filledOptions.length > 0 ? filledOptions : null,
        correct_answer: filledOptions.length > 0 ? formData.correct_answer : null,
        time_limit: formData.time_limit || null
      };

      await assessmentService.updateQuestion(questionId, questionData);
      toast.success('Question updated successfully');
      navigate(`/question-bank/${questionId}`);
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleOptionChange = (index, value) => {
    const newOptions = [...formData.options];
    newOptions[index] = value;
    setFormData(prev => ({
      ...prev,
      options: newOptions
    }));
    
    if (errors.options) {
      setErrors(prev => ({ ...prev, options: '' }));
    }
  };

  const addOption = () => {
    setFormData(prev => ({
      ...prev,
      options: [...prev.options, '']
    }));
  };

  const removeOption = (index) => {
    if (formData.options.length > 2) {
      const newOptions = formData.options.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        options: newOptions
      }));
    }
  };

  if (isLoading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container-fluid py-4">
          <div className="text-center py-5">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container-fluid py-4">
          <div className="text-center py-5">
            <i className="bi bi-exclamation-triangle fs-1 text-muted mb-3"></i>
            <h5 className="text-muted">Question not found</h5>
            <Link to="/question-bank" className="btn btn-primary">
              Back to Question Bank
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      <div className="container-fluid py-4">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            {/* Header */}
            <div className="mb-4">
              <nav aria-label="breadcrumb">
                <ol className="breadcrumb">
                  <li className="breadcrumb-item">
                    <Link to="/question-bank">Question Bank</Link>
                  </li>
                  <li className="breadcrumb-item">
                    <Link to={`/question-bank/${questionId}`}>Question Details</Link>
                  </li>
                  <li className="breadcrumb-item active" aria-current="page">
                    Edit
                  </li>
                </ol>
              </nav>
              <h1 className="h3 mb-0">Edit Question</h1>
              <p className="text-muted">Modify question details</p>
            </div>

            {/* Form */}
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Question Details</h5>
              </div>
              <div className="card-body">
                <form onSubmit={handleSubmit}>
                  {/* Question Content */}
                  <div className="mb-4">
                    <label htmlFor="content" className="form-label">
                      Question Content <span className="text-danger">*</span>
                    </label>
                    <textarea
                      className={`form-control ${errors.content ? 'is-invalid' : ''}`}
                      id="content"
                      rows="4"
                      placeholder="Enter your question here..."
                      value={formData.content}
                      onChange={(e) => handleInputChange('content', e.target.value)}
                    />
                    {errors.content && (
                      <div className="invalid-feedback">{errors.content}</div>
                    )}
                  </div>

                  {/* Specialization and Difficulty */}
                  <div className="row mb-4">
                    <div className="col-md-6">
                      <label htmlFor="specialization" className="form-label">
                        Specialization <span className="text-danger">*</span>
                      </label>
                      <select
                        className={`form-select ${errors.specialization ? 'is-invalid' : ''}`}
                        id="specialization"
                        value={formData.specialization}
                        onChange={(e) => handleInputChange('specialization', e.target.value)}
                      >
                        {specializations.map(spec => (
                          <option key={spec.value} value={spec.value}>
                            {spec.label}
                          </option>
                        ))}
                      </select>
                      {errors.specialization && (
                        <div className="invalid-feedback">{errors.specialization}</div>
                      )}
                    </div>
                    <div className="col-md-6">
                      <label htmlFor="difficulty" className="form-label">Difficulty Level</label>
                      <select
                        className="form-select"
                        id="difficulty"
                        value={formData.difficulty}
                        onChange={(e) => handleInputChange('difficulty', e.target.value)}
                      >
                        {difficulties.map(diff => (
                          <option key={diff.value} value={diff.value}>
                            {diff.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Answer Options */}
                  <div className="mb-4">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <label className="form-label mb-0">
                        Answer Options
                        <small className="text-muted ms-2">(Leave blank for open-ended questions)</small>
                      </label>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-primary"
                        onClick={addOption}
                      >
                        <i className="bi bi-plus-circle me-1"></i>
                        Add Option
                      </button>
                    </div>
                    
                    {formData.options.map((option, index) => (
                      <div key={index} className="mb-2">
                        <div className="input-group">
                          <span className="input-group-text">
                            {String.fromCharCode(65 + index)}
                          </span>
                          <input
                            type="text"
                            className="form-control"
                            placeholder={`Option ${String.fromCharCode(65 + index)}`}
                            value={option}
                            onChange={(e) => handleOptionChange(index, e.target.value)}
                          />
                          {formData.options.length > 2 && (
                            <button
                              type="button"
                              className="btn btn-outline-danger"
                              onClick={() => removeOption(index)}
                            >
                              <i className="bi bi-trash"></i>
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {errors.options && (
                      <div className="text-danger small mt-1">{errors.options}</div>
                    )}
                  </div>

                  {/* Correct Answer (for multiple choice) */}
                  {formData.options.some(option => option.trim()) && (
                    <div className="mb-4">
                      <label htmlFor="correct_answer" className="form-label">
                        Correct Answer <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className={`form-control ${errors.correct_answer ? 'is-invalid' : ''}`}
                        id="correct_answer"
                        placeholder="Enter the correct answer exactly as written above"
                        value={formData.correct_answer}
                        onChange={(e) => handleInputChange('correct_answer', e.target.value)}
                      />
                      {errors.correct_answer && (
                        <div className="invalid-feedback">{errors.correct_answer}</div>
                      )}
                      <div className="form-text">
                        Must match exactly one of the options above
                      </div>
                    </div>
                  )}

                  {/* Explanation */}
                  <div className="mb-4">
                    <label htmlFor="explanation" className="form-label">Explanation</label>
                    <textarea
                      className="form-control"
                      id="explanation"
                      rows="3"
                      placeholder="Provide an explanation for the correct answer (optional)"
                      value={formData.explanation}
                      onChange={(e) => handleInputChange('explanation', e.target.value)}
                    />
                  </div>

                  {/* Time Limit */}
                  <div className="mb-4">
                    <label htmlFor="time_limit" className="form-label">Time Limit (seconds)</label>
                    <Input
                      type="number"
                      id="time_limit"
                      min="10"
                      max="3600"
                      placeholder="60"
                      value={formData.time_limit}
                      onChange={(e) => handleInputChange('time_limit', parseInt(e.target.value) || '')}
                      error={errors.time_limit}
                    />
                    <div className="form-text">
                      Time limit for answering this question (10-3600 seconds)
                    </div>
                  </div>

                  {/* Form Actions */}
                  <div className="d-flex justify-content-between">
                    <Link to={`/question-bank/${questionId}`} className="btn btn-outline-secondary">
                      <i className="bi bi-arrow-left me-2"></i>
                      Cancel
                    </Link>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      <i className="bi bi-check-circle me-2"></i>
                      Update Question
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionBankEditQuestion;
