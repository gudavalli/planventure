import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../Navigation';
import Button from '../Button';
import Input from '../Input';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const CreateQuestion = () => {
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [questionType, setQuestionType] = useState('aptitude');  const [formData, setFormData] = useState({
    specialization: 'aptitude',
    content: '',
    options: ['', '', '', ''],
    correct_answer: null,
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
      });
    } else if (type === 'reading_comprehension') {
      setFormData({
        specialization: 'reading_comprehension',
        content: formData.content,
        options: ['', '', '', ''],
        correct_answer: null,
      });
    } else if (type === 'typing') {
      setFormData({
        specialization: 'typing',
        content: formData.content,
        options: null,
        correct_answer: null,
      });
    }
  };
    const handleOptionChange = (index, value) => {
    const newOptions = [...formData.options];
    newOptions[index] = value;
    
    // If this is the correct answer and it's being emptied, clear the correct_answer
    let updatedFormData = { ...formData, options: newOptions };
    if (formData.correct_answer === index && !value.trim()) {
      updatedFormData.correct_answer = null;
    }
    
    setFormData(updatedFormData);
    
    // Clear options error
    if (errors.options) {
      setErrors(prev => ({ ...prev, options: '' }));
    }
    
    // Clear correct_answer error if we had one
    if (errors.correct_answer) {
      setErrors(prev => ({ ...prev, correct_answer: '' }));
    }
  };
  
  const addOption = () => {
    setFormData(prev => ({
      ...prev,
      options: [...prev.options, '']
    }));
  };
    const removeOption = (index) => {
    // Don't allow removing if only 2 options remain
    if (formData.options.length <= 2) {
      toast.error('Question must have at least 2 options');
      return;
    }
    
    const newOptions = [...formData.options];
    newOptions.splice(index, 1);
    
    // Update correct_answer if needed
    let newCorrectAnswer = formData.correct_answer;
    if (formData.correct_answer === index) {
      // If the removed option was selected as correct, reset
      newCorrectAnswer = null;
    } else if (formData.correct_answer !== null && formData.correct_answer > index) {
      // If a later option was selected, shift the index down
      newCorrectAnswer = formData.correct_answer - 1;
    }
    
    setFormData(prev => ({
      ...prev,
      options: newOptions,
      correct_answer: newCorrectAnswer
    }));
  };
  
  const validate = () => {
    const newErrors = {};
    
    if (!formData.content.trim()) {
      newErrors.content = 'Question content is required';
    }
      if (questionType === 'aptitude' || questionType === 'reading_comprehension') {
      // Check all options have values
      const emptyOptions = formData.options.findIndex(opt => !opt.trim());
      if (emptyOptions !== -1) {
        newErrors.options = `Option ${emptyOptions + 1} cannot be empty`;
      }
      
      // Make sure a correct answer is selected
      if (formData.correct_answer === null) {
        newErrors.correct_answer = 'Please select the correct answer';
      }
      // Make sure the selected correct answer is not empty
      else if (formData.correct_answer !== null && 
              (!formData.options[formData.correct_answer] || 
               !formData.options[formData.correct_answer].trim())) {
        newErrors.correct_answer = 'The selected correct answer cannot be empty';
      }
    }
    
    if (questionType === 'reading_comprehension' && !readingParagraph.trim()) {
      newErrors.readingParagraph = 'Reading passage is required';
    }
    
    if (questionType === 'typing' && formData.content.length < 50) {
      newErrors.content = 'Typing text must be at least 50 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
      setIsSubmitting(true);
    try {
      let questionData = {
        ...formData
      };
      
      // For multiple choice questions, convert the correct_answer index to the actual option text
      if ((questionType === 'aptitude' || questionType === 'reading_comprehension') && 
          formData.correct_answer !== null) {
        questionData.correct_answer = formData.options[formData.correct_answer];
      }
      
      let response;
      
      // For reading comprehension, create reading set first
      if (questionType === 'reading_comprehension') {
        // Create a reading set with the paragraph
        response = await assessmentService.createReadingSet({
          paragraph: readingParagraph
        });
        
        // Then create the question with the reading set ID
        questionData.reading_set_id = response.id;
      }
      
      response = await assessmentService.createQuestion(questionData);
      
      toast.success('Question created successfully');
      navigate('/assessments/questions');
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
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow-sm">
              <div className="card-header bg-white py-3">
                <h5 className="mb-0">Create Question</h5>
              </div>
              
              <div className="card-body p-4">
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
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
                      {questionType === 'aptitude' && 'Multiple choice question with one correct answer'}
                      {questionType === 'reading_comprehension' && 'Question based on a reading passage'}
                      {questionType === 'typing' && 'Typing speed and accuracy test'}
                    </div>
                  </div>
                  
                  {/* Reading Comprehension Paragraph */}
                  {questionType === 'reading_comprehension' && (
                    <div className="mb-4">
                      <label className="form-label">Reading Passage</label>
                      <textarea
                        className={`form-control ${errors.readingParagraph ? 'is-invalid' : ''}`}
                        rows="6"
                        value={readingParagraph}
                        onChange={(e) => setReadingParagraph(e.target.value)}
                        placeholder="Enter the reading passage here..."
                      ></textarea>
                      {errors.readingParagraph && (
                        <div className="invalid-feedback">
                          {errors.readingParagraph}
                        </div>
                      )}
                      <div className="form-text">
                        The passage that candidates will read before answering the question.
                      </div>
                    </div>
                  )}
                  
                  {/* Question Content */}
                  <div className="mb-4">
                    <label className="form-label">
                      {questionType === 'typing' ? 'Typing Text' : 'Question'}
                    </label>
                    <textarea
                      className={`form-control ${errors.content ? 'is-invalid' : ''}`}
                      name="content"
                      rows={questionType === 'typing' ? 5 : 3}
                      value={formData.content}
                      onChange={handleChange}
                      placeholder={questionType === 'typing' 
                        ? "Enter the text that candidates will type (min. 50 characters)..." 
                        : "Enter your question here..."
                      }
                    ></textarea>
                    {errors.content && (
                      <div className="invalid-feedback">
                        {errors.content}
                      </div>
                    )}
                  </div>
                  
                  {/* Options for Multiple Choice and Reading Comprehension */}
                  {(questionType === 'aptitude' || questionType === 'reading_comprehension') && (
                    <div className="mb-4">
                      <label className="form-label">Answer Options</label>
                        {formData.options.map((option, index) => (                        <div className="input-group mb-2" key={index}>
                          <div className="input-group-text">
                            <input
                              type="radio"
                              name="correct_answer"
                              checked={formData.correct_answer === index}
                              onChange={() => setFormData(prev => ({ ...prev, correct_answer: index }))}
                              // Removed the disabled condition to always allow selection
                            />
                          </div>
                          <input
                            type="text"
                            className="form-control"
                            placeholder={`Option ${index + 1}`}
                            value={option}
                            onChange={(e) => handleOptionChange(index, e.target.value)}
                          />
                          <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={() => removeOption(index)}
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        </div>
                      ))}
                        {errors.options && (
                        <div className="text-danger mb-2 small">
                          {errors.options}
                        </div>
                      )}
                      
                      {errors.correct_answer && (
                        <div className="alert alert-danger py-2 mt-2 mb-2">
                          <i className="bi bi-exclamation-triangle-fill me-2"></i>
                          {errors.correct_answer}
                        </div>
                      )}
                      
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary"
                        onClick={addOption}
                      >
                        <i className="bi bi-plus-circle me-1"></i> Add Option
                      </button>
                    </div>
                  )}
                  
                  <div className="d-flex justify-content-between mt-4">
                    <Button
                      type="button"
                      variant="light"
                      onClick={() => navigate('/assessments/questions')}
                    >
                      Cancel
                    </Button>
                    
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                    >
                      Create Question
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

export default CreateQuestion;
