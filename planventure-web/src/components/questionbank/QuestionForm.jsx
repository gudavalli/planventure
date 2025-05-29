import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import Button from '../Button';
import Input from '../Input';
import toast from 'react-hot-toast';

const QuestionForm = ({ 
  mode = 'create', // 'create' or 'edit'
  questionId = null,
  onSuccess = null 
}) => {
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [question, setQuestion] = useState(null);
  const [questionType, setQuestionType] = useState('aptitude');
  const [readingParagraph, setReadingParagraph] = useState('');  const [formData, setFormData] = useState({
    content: '',
    specialization: 'aptitude',
    options: ['', '', '', ''],
    correct_answer: null,
    explanation: '',
    difficulty: 'medium',
    time_limit: 60,
  });
  const [isLoading, setIsLoading] = useState(mode === 'edit');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  const questionTypes = [
    { value: 'aptitude', label: 'Multiple Choice' },
    { value: 'reading_comprehension', label: 'Reading Comprehension' },
    { value: 'typing', label: 'Typing Test' }
  ];

  const specializations = [
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
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];

  // Fetch question data for edit mode
  const fetchQuestion = useCallback(async () => {
    if (mode !== 'edit' || !questionId) return;
    
    setIsLoading(true);
    try {
      const data = await assessmentService.getQuestionDetails(questionId);
      setQuestion(data);
      
      // Determine question type from data
      let detectedType = 'aptitude';
      if (data.specialization === 'reading_comprehension') {
        detectedType = 'reading_comprehension';
      } else if (data.specialization === 'typing') {
        detectedType = 'typing';
      }
      setQuestionType(detectedType);

      // Set reading paragraph if it's a reading comprehension question
      if (data.reading_set && data.reading_set.content) {
        setReadingParagraph(data.reading_set.content);
      }      // Prepare form data
      const isMultipleChoice = Array.isArray(data.options) && data.options.length > 0;
      let correctAnswerIndex = null;
      if (isMultipleChoice && data.correct_answer) {
        const answerIndex = data.options.findIndex(option => option === data.correct_answer);
        if (answerIndex !== -1) {
          correctAnswerIndex = answerIndex;
        }
      }

      setFormData({
        content: data.content || '',
        specialization: data.specialization || 'aptitude',
        options: isMultipleChoice ? data.options : ['', '', '', ''],
        correct_answer: correctAnswerIndex,
        explanation: data.explanation || '',
        difficulty: data.difficulty || 'medium',
        time_limit: data.time_limit || 60
      });
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [mode, questionId, handleError]);

  useEffect(() => {
    fetchQuestion();
  }, [fetchQuestion]);
  // Handle question type change (create mode only)
  const handleTypeChange = (newType) => {
    setQuestionType(newType);
    setFormData(prev => ({
      ...prev,
      specialization: newType,
      options: newType === 'aptitude' ? ['', '', '', ''] : [],
      correct_answer: null
    }));
    setReadingParagraph('');
    setErrors({});
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.content.trim()) {
      newErrors.content = 'Question content is required';
    }

    if (!formData.specialization) {
      newErrors.specialization = 'Specialization is required';
    }

    // Reading comprehension specific validation
    if (questionType === 'reading_comprehension' && !readingParagraph.trim()) {
      newErrors.readingParagraph = 'Reading passage is required for reading comprehension questions';
    }

    // Typing test specific validation
    if (questionType === 'typing' && formData.content.length < 50) {
      newErrors.content = 'Typing test content must be at least 50 characters long';
    }

    // Multiple choice specific validation
    if (questionType === 'aptitude') {
      const filledOptions = formData.options.filter(option => option.trim());
      if (filledOptions.length < 2) {
        newErrors.options = 'Please provide at least 2 options for multiple choice questions';
      }
        if (formData.correct_answer === null || formData.correct_answer === undefined) {
        newErrors.correct_answer = 'Please select the correct answer by clicking on one of the option letters';
      } else if (formData.correct_answer >= filledOptions.length) {
        newErrors.correct_answer = 'Selected answer option does not exist';
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
      let questionData = { ...formData };      // Handle multiple choice questions
      if (questionType === 'aptitude') {
        const filledOptions = formData.options.filter(option => option.trim());
        questionData.options = filledOptions;
        
        // Convert index-based correct_answer to option text
        if (formData.correct_answer !== null && formData.correct_answer >= 0 && 
            formData.correct_answer < filledOptions.length) {
          questionData.correct_answer = filledOptions[formData.correct_answer];
        } else {
          questionData.correct_answer = null;
        }
      } else {
        questionData.options = null;
        questionData.correct_answer = null;
      }

      // Handle reading comprehension questions
      if (questionType === 'reading_comprehension') {
        questionData.reading_set = {
          content: readingParagraph
        };
      }

      // API call based on mode
      if (mode === 'create') {
        await assessmentService.createQuestion(questionData);
        toast.success('Question created successfully');
        if (onSuccess) {
          onSuccess();
        } else {
          navigate('/question-bank');
        }
      } else {
        await assessmentService.updateQuestion(questionId, questionData);
        toast.success('Question updated successfully');
        if (onSuccess) {
          onSuccess();
        } else {
          navigate(`/question-bank/${questionId}`);
        }
      }
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
    setFormData(prev => {
      let newCorrectAnswer = prev.correct_answer;
      if (!value.trim() && prev.correct_answer === index) {
        newCorrectAnswer = null;
      }
      
      return {
        ...prev,
        options: newOptions,
        correct_answer: newCorrectAnswer
      };
    });
    
    if (errors.options) {
      setErrors(prev => ({ ...prev, options: '' }));
    }
  };

  const addOption = () => {
    if (formData.options.length < 6) {
      setFormData(prev => ({
        ...prev,
        options: [...prev.options, '']
      }));
    }
  };
  const removeOption = (index) => {
    if (formData.options.length > 2) {
      const newOptions = formData.options.filter((_, i) => i !== index);
      setFormData(prev => {
        let newCorrectAnswer = prev.correct_answer;
        if (prev.correct_answer === index) {
          newCorrectAnswer = null;
        } else if (prev.correct_answer !== null && prev.correct_answer > index) {
          newCorrectAnswer = prev.correct_answer - 1;
        }
        
        return {
          ...prev,
          options: newOptions,
          correct_answer: newCorrectAnswer
        };
      });
    }
  };
  // Loading state for edit mode
  if (isLoading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  // Not found state for edit mode
  if (mode === 'edit' && !question) {
    return (
      <div className="text-center py-5">
        <i className="bi bi-exclamation-triangle fs-1 text-muted mb-3"></i>
        <h5 className="text-muted">Question not found</h5>
        <Link to="/question-bank" className="btn btn-primary">
          Back to Question Bank
        </Link>
      </div>
    );
  }

  const pageTitle = mode === 'create' ? 'Create Question' : 'Edit Question';
  const submitButtonText = mode === 'create' ? 'Create Question' : 'Update Question';
  const cancelPath = mode === 'create' ? '/question-bank' : `/question-bank/${questionId}`;

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        {/* Header */}
        <div className="mb-4">
          <h1 className="h3 mb-0">{pageTitle}</h1>
          <p className="text-muted">
            {mode === 'create' 
              ? 'Add a new question to the question bank' 
              : 'Modify question details'
            }
          </p>
            </div>

            {/* Form */}
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">Question Details</h5>
              </div>
              <div className="card-body">
                <form onSubmit={handleSubmit}>
                  {/* Question Type (Create mode only) */}
                  {mode === 'create' && (
                    <div className="mb-4">
                      <label htmlFor="questionType" className="form-label">
                        Question Type <span className="text-danger">*</span>
                      </label>
                      <select
                        className="form-select"
                        id="questionType"
                        value={questionType}
                        onChange={(e) => handleTypeChange(e.target.value)}
                      >
                        {questionTypes.map(type => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Reading Paragraph (Reading Comprehension only) */}
                  {questionType === 'reading_comprehension' && (
                    <div className="mb-4">
                      <label htmlFor="readingParagraph" className="form-label">
                        Reading Passage <span className="text-danger">*</span>
                      </label>
                      <textarea
                        className={`form-control ${errors.readingParagraph ? 'is-invalid' : ''}`}
                        id="readingParagraph"
                        rows="6"
                        placeholder="Enter the reading passage here..."
                        value={readingParagraph}
                        onChange={(e) => {
                          setReadingParagraph(e.target.value);
                          if (errors.readingParagraph) {
                            setErrors(prev => ({ ...prev, readingParagraph: '' }));
                          }
                        }}
                      />
                      {errors.readingParagraph && (
                        <div className="invalid-feedback">{errors.readingParagraph}</div>
                      )}
                    </div>
                  )}

                  {/* Question Content */}
                  <div className="mb-4">
                    <label htmlFor="content" className="form-label">
                      {questionType === 'typing' ? 'Typing Text' : 'Question Content'} <span className="text-danger">*</span>
                    </label>
                    <textarea
                      className={`form-control ${errors.content ? 'is-invalid' : ''}`}
                      id="content"
                      rows={questionType === 'typing' ? "6" : "4"}
                      placeholder={
                        questionType === 'typing' 
                          ? "Enter the text for typing test (minimum 50 characters)..."
                          : "Enter your question here..."
                      }
                      value={formData.content}
                      onChange={(e) => handleInputChange('content', e.target.value)}
                    />
                    {errors.content && (
                      <div className="invalid-feedback">{errors.content}</div>
                    )}
                    {questionType === 'typing' && (
                      <div className="form-text">
                        Character count: {formData.content.length} (minimum 50 required)
                      </div>
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
                        disabled={mode === 'create'} // Auto-set based on question type in create mode
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

                  {/* Answer Options (Multiple Choice only) */}
                  {questionType === 'aptitude' && (
                    <div className="mb-4">
                      <div className="d-flex justify-content-between align-items-center mb-3">
                        <label className="form-label mb-0">Answer Options</label>
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-primary"
                          onClick={addOption}
                          disabled={formData.options.length >= 6}
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

                      {/* Correct Answer Selection */}
                      {formData.options.some(option => option.trim()) && (
                        <div className="mt-3">
                          <label className="form-label">
                            Correct Answer <span className="text-danger">*</span>
                          </label>
                          <p className="text-muted small mb-2">
                            Click on the letter (A, B, C, D) to mark the correct answer. The selected letter will turn green.
                          </p>
                          <div className="d-flex gap-2 mb-2">
                            {formData.options.map((option, index) => {
                              if (!option.trim()) return null;
                              return (
                                <button
                                  key={index}
                                  type="button"
                                  className={`btn ${formData.correct_answer === index ? 'btn-success text-white' : 'btn-outline-secondary'}`}
                                  style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: '50%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontWeight: 'bold'
                                  }}
                                  onClick={() => setFormData(prev => ({ ...prev, correct_answer: index }))}
                                  title={`Select option ${String.fromCharCode(65 + index)} as correct answer`}
                                >
                                  {String.fromCharCode(65 + index)}
                                </button>
                              );
                            })}
                          </div>
                          {errors.correct_answer && (
                            <div className="text-danger small">{errors.correct_answer}</div>
                          )}
                        </div>
                      )}
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
                    <Link to={cancelPath} className="btn btn-outline-secondary">
                      <i className="bi bi-arrow-left me-2"></i>
                      Cancel
                    </Link>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      <i className="bi bi-check-circle me-2"></i>
                      {submitButtonText}
                    </Button>                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
  );
};

export default QuestionForm;
