import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const QuestionBankCreateQuestion = () => {
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [questionType, setQuestionType] = useState('aptitude');
  const [formData, setFormData] = useState({
    specialization: 'aptitude',
    content: '',
    options: ['', '', '', ''],
    correct_answer: null,
    explanation: '',
    difficulty: 'medium',
    time_limit: 60,
  });
  const [errors, setErrors] = useState({});
  const [readingParagraph, setReadingParagraph] = useState('');
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };
  
  const handleTypeChange = (e) => {
    const type = e.target.value;
    setQuestionType(type);
    
    // Reset form when changing question type
    if (type === 'aptitude') {
      setFormData({
        specialization: 'aptitude',
        content: formData.content,
        options: ['', '', '', ''],
        correct_answer: null,
        explanation: formData.explanation,
        difficulty: formData.difficulty,
        time_limit: formData.time_limit,
      });
    } else if (type === 'reading_comprehension') {
      setFormData({
        specialization: 'reading_comprehension',
        content: formData.content,
        options: ['', '', '', ''],
        correct_answer: null,
        explanation: formData.explanation,
        difficulty: formData.difficulty,
        time_limit: formData.time_limit,
      });
    } else if (type === 'typing') {
      setFormData({
        specialization: 'typing',
        content: formData.content,
        options: null,
        correct_answer: null,
        explanation: formData.explanation,
        difficulty: formData.difficulty,
        time_limit: formData.time_limit,
      });
    }
  };

  const handleOptionChange = (index, value) => {
    const newOptions = [...formData.options];
    newOptions[index] = value;
    setFormData(prev => ({ ...prev, options: newOptions }));
  };

  const handleCorrectAnswerChange = (e) => {
    const index = parseInt(e.target.value);
    setFormData(prev => ({ 
      ...prev, 
      correct_answer: prev.options[index] 
    }));
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
        options: newOptions,
        correct_answer: newOptions.includes(prev.correct_answer) ? prev.correct_answer : null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.content.trim()) {
      newErrors.content = 'Question content is required';
    }

    if (questionType === 'reading_comprehension' && !readingParagraph.trim()) {
      newErrors.readingParagraph = 'Reading passage is required for reading comprehension questions';
    }

    if (questionType !== 'typing') {
      if (!formData.options.some(option => option.trim())) {
        newErrors.options = 'At least one option is required';
      }

      if (!formData.correct_answer) {
        newErrors.correct_answer = 'Please select the correct answer';
      }
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
      const submitData = {
        ...formData,
        options: questionType === 'typing' ? null : formData.options.filter(opt => opt.trim()),
      };

      // Add reading set if it's a reading comprehension question
      if (questionType === 'reading_comprehension' && readingParagraph.trim()) {
        submitData.reading_set = {
          paragraph: readingParagraph.trim()
        };
      }

      await assessmentService.createQuestion(submitData);
      toast.success('Question created successfully');
      navigate('/question-bank');
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        {/* Header */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div className="d-flex align-items-center">
            <Button 
              variant="outline-secondary" 
              className="me-3"
              onClick={() => navigate('/question-bank')}
            >
              <i className="bi bi-arrow-left"></i>
            </Button>
            <div>
              <h1 className="h3 mb-1">Create New Question</h1>
              <p className="text-muted mb-0">Add a new question to your question bank</p>
            </div>
          </div>
        </div>

        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow-sm">
              <div className="card-header bg-white py-3">
                <h5 className="mb-0">Question Details</h5>
              </div>
              
              <div className="card-body p-4">
                <form onSubmit={handleSubmit}>
                  {/* Question Type Selection */}
                  <div className="mb-4">
                    <label className="form-label">Question Type</label>
                    <select 
                      className="form-select"
                      value={questionType}
                      onChange={handleTypeChange}
                    >
                      <option value="aptitude">Multiple Choice</option>
                      <option value="reading_comprehension">Reading Comprehension</option>
                      <option value="typing">Typing Test</option>
                    </select>
                    <div className="form-text">
                      {questionType === 'aptitude' && 'Create multiple choice questions with various answer options.'}
                      {questionType === 'reading_comprehension' && 'Create questions based on reading passages.'}
                      {questionType === 'typing' && 'Create typing tests where candidates type specific text.'}
                    </div>
                  </div>

                  {/* Specialization/Subject */}
                  <div className="mb-3">
                    <label htmlFor="specialization" className="form-label">Subject/Specialization</label>
                    <Input
                      id="specialization"
                      name="specialization"
                      type="text"
                      className="form-control"
                      value={formData.specialization}
                      onChange={handleChange}
                      placeholder={questionType === 'typing' ? 'typing' : 'e.g., JavaScript, React, General Knowledge'}
                      required
                    />
                    <div className="form-text">
                      Specify the subject area or technology this question focuses on.
                    </div>
                  </div>

                  {/* Reading Passage (for reading comprehension) */}
                  {questionType === 'reading_comprehension' && (
                    <div className="mb-4">
                      <label htmlFor="readingParagraph" className="form-label">Reading Passage</label>
                      <textarea
                        id="readingParagraph"
                        className={`form-control ${errors.readingParagraph ? 'is-invalid' : ''}`}
                        value={readingParagraph}
                        onChange={(e) => setReadingParagraph(e.target.value)}
                        rows="6"
                        placeholder="Enter the reading passage that candidates will read before answering questions..."
                        required
                      />
                      {errors.readingParagraph && (
                        <div className="invalid-feedback">{errors.readingParagraph}</div>
                      )}
                      <div className="form-text">
                        Provide the text that candidates will need to read and understand.
                      </div>
                    </div>
                  )}

                  {/* Question Content */}
                  <div className="mb-4">
                    <label htmlFor="content" className="form-label">Question Content</label>
                    <textarea
                      id="content"
                      name="content"
                      className={`form-control ${errors.content ? 'is-invalid' : ''}`}
                      value={formData.content}
                      onChange={handleChange}
                      rows="5"
                      placeholder={
                        questionType === 'typing' 
                          ? 'Enter the text that candidates will need to type exactly...'
                          : 'Enter your question here. Be clear and specific...'
                      }
                      required
                    />
                    {errors.content && (
                      <div className="invalid-feedback">{errors.content}</div>
                    )}
                    <div className="form-text">
                      {questionType === 'typing' 
                        ? 'The exact text that candidates will need to type.'
                        : 'Write a clear, concise question. Use proper grammar and punctuation.'
                      }
                    </div>
                  </div>
                  
                  {/* Answer Options (for multiple choice questions) */}
                  {questionType !== 'typing' && (
                    <div className="mb-4">
                      <label className="form-label">Answer Options</label>
                      {formData.options.map((option, index) => (
                        <div key={index} className="input-group mb-2">
                          <span className="input-group-text">{String.fromCharCode(65 + index)}</span>
                          <input
                            type="text"
                            className="form-control"
                            value={option}
                            onChange={(e) => handleOptionChange(index, e.target.value)}
                            placeholder={`Option ${String.fromCharCode(65 + index)}`}
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
                      ))}
                      {errors.options && (
                        <div className="text-danger small mb-2">{errors.options}</div>
                      )}
                      
                      {formData.options.length < 6 && (
                        <button
                          type="button"
                          className="btn btn-outline-primary btn-sm"
                          onClick={addOption}
                        >
                          <i className="bi bi-plus-circle me-1"></i>Add Option
                        </button>
                      )}
                    </div>
                  )}

                  {/* Correct Answer Selection */}
                  {questionType !== 'typing' && formData.options.some(opt => opt.trim()) && (
                    <div className="mb-4">
                      <label className="form-label">Correct Answer</label>
                      <select
                        className={`form-select ${errors.correct_answer ? 'is-invalid' : ''}`}
                        onChange={handleCorrectAnswerChange}
                        value={formData.options.findIndex(opt => opt === formData.correct_answer)}
                      >
                        <option value="">Select the correct answer</option>
                        {formData.options.map((option, index) => (
                          option.trim() && (
                            <option key={index} value={index}>
                              {String.fromCharCode(65 + index)}. {option}
                            </option>
                          )
                        ))}
                      </select>
                      {errors.correct_answer && (
                        <div className="invalid-feedback">{errors.correct_answer}</div>
                      )}
                    </div>
                  )}

                  {/* Question Metadata */}
                  <div className="row mb-4">
                    <div className="col-md-4">
                      <label htmlFor="difficulty" className="form-label">Difficulty Level</label>
                      <select
                        id="difficulty"
                        name="difficulty"
                        className="form-select"
                        value={formData.difficulty}
                        onChange={handleChange}
                      >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                      </select>
                    </div>

                    <div className="col-md-4">
                      <label htmlFor="time_limit" className="form-label">Time Limit (seconds)</label>
                      <Input
                        id="time_limit"
                        name="time_limit"
                        type="number"
                        className="form-control"
                        value={formData.time_limit}
                        onChange={handleChange}
                        min="30"
                        max="3600"
                      />
                    </div>
                  </div>

                  {/* Explanation */}
                  <div className="mb-4">
                    <label htmlFor="explanation" className="form-label">Explanation (Optional)</label>
                    <textarea
                      id="explanation"
                      name="explanation"
                      className="form-control"
                      value={formData.explanation}
                      onChange={handleChange}
                      rows="3"
                      placeholder="Provide an explanation for the correct answer or additional context..."
                    />
                    <div className="form-text">
                      Help candidates understand why the answer is correct (shown after completion).
                    </div>
                  </div>

                  {/* Submit Buttons */}
                  <div className="d-flex justify-content-between">
                    <Button
                      type="button"
                      variant="outline-secondary"
                      onClick={() => navigate('/question-bank')}
                    >
                      Cancel
                    </Button>
                    <div className="d-flex gap-2">
                      <Button
                        type="submit"
                        variant="primary"
                        isLoading={isSubmitting}
                        disabled={isSubmitting}
                      >
                        Create Question
                      </Button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>

          {/* Help Sidebar */}
          <div className="col-lg-4">
            <div className="card bg-light">
              <div className="card-header bg-transparent">
                <h6 className="mb-0">
                  <i className="bi bi-lightbulb me-1"></i>Question Writing Tips
                </h6>
              </div>
              <div className="card-body">
                <ul className="list-unstyled mb-0 small">
                  <li className="mb-2">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Write clear, concise questions
                  </li>
                  <li className="mb-2">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Avoid ambiguous wording
                  </li>
                  <li className="mb-2">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Make all wrong answers plausible
                  </li>
                  <li className="mb-2">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Test one concept per question
                  </li>
                  <li className="mb-2">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Use proper grammar and punctuation
                  </li>
                  <li className="mb-0">
                    <i className="bi bi-check-circle text-success me-1"></i>
                    Provide helpful explanations
                  </li>
                </ul>
              </div>
            </div>

            <div className="card bg-light mt-3">
              <div className="card-header bg-transparent">
                <h6 className="mb-0">
                  <i className="bi bi-info-circle me-1"></i>Question Types
                </h6>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <strong>Multiple Choice</strong>
                  <p className="small text-muted mb-0">
                    General knowledge, technical skills, logical reasoning
                  </p>
                </div>
                <div className="mb-3">
                  <strong>Reading Comprehension</strong>
                  <p className="small text-muted mb-0">
                    Text analysis, understanding, critical thinking
                  </p>
                </div>
                <div className="mb-0">
                  <strong>Typing Test</strong>
                  <p className="small text-muted mb-0">
                    Typing speed, accuracy, data entry skills
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionBankCreateQuestion;
