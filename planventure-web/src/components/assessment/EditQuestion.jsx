import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import Button from '../Button';
import Input from '../Input';
import Navigation from '../Navigation';
import toast from 'react-hot-toast';

const EditQuestion = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [question, setQuestion] = useState(null);
  const [formData, setFormData] = useState({
    content: '',
    specialization: '',
    options: [],
    correct_answer: null,
    explanation: '',
    difficulty: 'medium',
    time_limit: 60
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
    useEffect(() => {
    const fetchQuestion = async () => {
      setIsLoading(true);      
      try {
        const data = await assessmentService.getQuestionDetails(questionId);
        console.log('Question data from API:', data);
        setQuestion(data);
        
        // Determine if this is a multiple choice question
        // If it has options array, treat it as a multiple choice question
        const isMultipleChoice = Array.isArray(data.options) && data.options.length > 0;
        
        // For multiple choice questions, ensure specialization is set to 'aptitude'
        let specialization = data.specialization || '';
        if (isMultipleChoice && specialization !== 'aptitude') {
          console.log('Question has options but specialization is not aptitude. Setting to aptitude.');
          specialization = 'aptitude';
        }
        
        // Convert correct_answer to index if it's option text
        let correctAnswerIndex = null;
        if (isMultipleChoice && data.correct_answer !== null) {
          if (typeof data.correct_answer === 'string') {
            // Find the matching option text
            correctAnswerIndex = data.options.findIndex(option => option === data.correct_answer);
            console.log('Converted correct_answer from text to index:', data.correct_answer, '->', correctAnswerIndex);
          } else if (typeof data.correct_answer === 'number' && data.correct_answer >= 0 && data.correct_answer < data.options.length) {
            // If it's already an index, use it directly
            correctAnswerIndex = data.correct_answer;
            console.log('Using correct_answer as index:', correctAnswerIndex);
          }
        }
        
        // Use empty array if options is null or undefined
        const options = isMultipleChoice ? data.options : [];
        
        setFormData({
          content: data.content || '',
          specialization: specialization,
          options: options,
          correct_answer: correctAnswerIndex,
          explanation: data.explanation || '',
          difficulty: data.difficulty || 'medium',
          time_limit: data.time_limit || 60,
          reading_set_id: data.reading_set_id || null
        });
        
        console.log('Form data set:', {
          content: data.content || '',
          specialization: specialization,
          options: data.options || [],
          correct_answer: correctAnswerIndex,
          explanation: data.explanation || '',
        });
      } catch (error) {
        handleError(error);
        navigate('/assessments/questions');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchQuestion();
  }, [questionId, navigate, handleError]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleOptionChange = (index, value) => {
    const updatedOptions = [...formData.options];
    updatedOptions[index] = value;
    setFormData(prev => ({
      ...prev,
      options: updatedOptions
    }));
  };
  
  const handleAddOption = () => {
    setFormData(prev => ({
      ...prev,
      options: [...prev.options, '']
    }));
  };
    const handleRemoveOption = (index) => {
    // Update the correct answer index if needed
    let newCorrectAnswer = formData.correct_answer;
    if (formData.correct_answer === index) {
      newCorrectAnswer = null;
    } else if (formData.correct_answer !== null && formData.correct_answer > index) {
      newCorrectAnswer = formData.correct_answer - 1;
    }
    
    setFormData(prev => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index),
      correct_answer: newCorrectAnswer
    }));
  };  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.content.trim()) {
      toast.error('Question content is required');
      return;
    }
    
    // Check if this is a multiple choice question
    const isMultipleChoice = formData.specialization === 'aptitude' || 
      (Array.isArray(formData.options) && formData.options.length > 0);
    
    if (isMultipleChoice) {
      if (formData.options.length < 2) {
        toast.error('Multiple choice questions require at least 2 options');
        return;
      }
      
      if (formData.correct_answer === null) {
        toast.error('Please select a correct answer');
        return;
      }
      
      // Check for empty options
      if (formData.options.some(option => !option.trim())) {
        toast.error('Options cannot be empty');
        return;
      }
    }
    
    console.log('Submitting form data:', formData);
    setIsSaving(true);
    try {
      // Prepare the data for submission
      let submissionData = { ...formData };
      
      // For multiple choice questions, convert the correct_answer index to the actual option text
      if (isMultipleChoice && formData.correct_answer !== null) {
        if (Array.isArray(formData.options) && 
            formData.correct_answer >= 0 && 
            formData.correct_answer < formData.options.length) {
          submissionData.correct_answer = formData.options[formData.correct_answer];
          console.log('Converting correct answer index to text:', formData.correct_answer, 
                      '->', submissionData.correct_answer);
        }
      }
      
      const response = await assessmentService.updateQuestion(questionId, submissionData);
      console.log('Update response:', response);
      toast.success('Question updated successfully');
      navigate('/assessments/questions');
    } catch (error) {
      console.error('Error updating question:', error);
      handleError(error);
    } finally {
      setIsSaving(false);
    }
  };
  
  if (isLoading) {
    return (
      <div className="min-vh-100 bg-light">
        <Navigation />
        <div className="container py-4">
          <div className="d-flex justify-content-center">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">Edit Question</h1>
        </div>
        
        <div className="card shadow-sm">
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="specialization" className="form-label">Question Type</label>
                <select
                  id="specialization"
                  name="specialization"
                  className="form-select"
                  value={formData.specialization}
                  onChange={handleInputChange}
                  disabled // Cannot change question type when editing
                >
                  <option value="aptitude">Multiple Choice</option>
                  <option value="reading_comprehension">Reading Comprehension</option>
                  <option value="typing">Typing Test</option>
                </select>              </div>
                <div className="mb-3">
                <label htmlFor="content" className="form-label">Question Content</label>
                <textarea
                  id="content"
                  name="content"
                  className="form-control"
                  value={formData.content}
                  onChange={handleInputChange}
                  rows="5"
                  required
                ></textarea>
                <div className="form-text">
                  {formData.specialization === 'typing' ? 
                    'Enter the text that the candidate will need to type.' : 
                    'Enter your question here. Be clear and concise.'}
                </div>
              </div>
              
              {/* Show options section for aptitude or any question with options */}
              {(formData.specialization === 'aptitude' || (Array.isArray(formData.options) && formData.options.length > 0)) && (
                <>
                  <div className="mb-3">
                    <label className="form-label">Options</label>
                    {formData.options.map((option, index) => (
                      <div key={index} className="input-group mb-2">
                        <div className="input-group-text">
                          <input
                            type="radio"
                            name="correct_answer"
                            checked={formData.correct_answer === index}
                            onChange={() => setFormData(prev => ({ ...prev, correct_answer: index }))}
                            aria-label={`Option ${index + 1} is correct`}
                          />
                        </div>
                        <input
                          type="text"
                          className="form-control"
                          value={option}
                          onChange={(e) => handleOptionChange(index, e.target.value)}
                          placeholder={`Option ${index + 1}`}
                          required
                        />
                        <button
                          type="button"
                          className="btn btn-outline-danger"
                          onClick={() => handleRemoveOption(index)}
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      </div>
                    ))}
                    
                    <button
                      type="button"
                      className="btn btn-outline-secondary"
                      onClick={handleAddOption}
                    >
                      <i className="bi bi-plus-circle me-2"></i>Add Option
                    </button>
                  </div>
                  
                  <div className="mb-3">
                    <label htmlFor="explanation" className="form-label">Explanation (Optional)</label>
                    <textarea
                      id="explanation"
                      name="explanation"
                      className="form-control"
                      value={formData.explanation}
                      onChange={handleInputChange}
                      rows="3"
                    ></textarea>
                    <div className="form-text">
                      Explain why the correct answer is correct. This will be shown to the candidate after they submit their answer.
                    </div>
                  </div>
                </>
              )}
              
              <div className="row mb-3">
                <div className="col-md-6">
                  <label htmlFor="difficulty" className="form-label">Difficulty</label>
                  <select
                    id="difficulty"
                    name="difficulty"
                    className="form-select"
                    value={formData.difficulty}
                    onChange={handleInputChange}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <div className="col-md-6">
                  <label htmlFor="time_limit" className="form-label">Time Limit (seconds)</label>
                  <input
                    type="number"
                    id="time_limit"
                    name="time_limit"
                    className="form-control"
                    value={formData.time_limit}
                    onChange={handleInputChange}
                    min="10"
                    max="300"
                  />
                </div>
              </div>
              
              <div className="d-flex justify-content-end gap-2">
                <Button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => navigate('/assessments/questions')}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="btn btn-primary"
                  isLoading={isSaving}
                  disabled={isSaving}
                >
                  Save Changes
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditQuestion;
