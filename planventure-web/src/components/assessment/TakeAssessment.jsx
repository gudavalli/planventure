import { useState, useEffect, useRef } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Button from '../Button';
import { assessmentService } from '../../services/api';
import { useApiErrorHandler } from '../../hooks/useApiErrorHandler';
import toast from 'react-hot-toast';

const TakeAssessment = () => {
  const { assessmentId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { handleError } = useApiErrorHandler();
  
  const [assessment, setAssessment] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState({
    current: 0,
    total: 0
  });
  const [timeRemaining, setTimeRemaining] = useState(null);
  const timerIntervalRef = useRef(null);
  const typingStartTimeRef = useRef(null);
  const typingCharactersRef = useRef(0);
  const typingErrorsRef = useRef(0);
  
  // Parse query parameters
  const queryParams = new URLSearchParams(location.search);
  const email = queryParams.get('email');
  const token = queryParams.get('token');
  
  useEffect(() => {
    if (!assessmentId || !email || !token) {
      toast.error('Invalid assessment link');
      navigate('/');
      return;
    }
    
    const loadAssessment = async () => {
      try {
        const assessmentData = await assessmentService.accessAssessment(assessmentId, email, token);
        setAssessment(assessmentData);
        
        if (assessmentData.status === 'in_progress') {
          loadCurrentQuestion();
        } else if (assessmentData.status === 'completed') {
          toast.success('Assessment already completed');
          navigate(`/assessment/results/${assessmentId}?email=${email}&token=${token}`);
        }
        
        setIsLoading(false);
      } catch (error) {
        handleError(error);
        navigate('/');
      }
    };
    
    loadAssessment();
    
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    };
  }, [assessmentId, email, token, navigate, handleError]);
  
  const startAssessment = async () => {
    setIsSubmitting(true);
    try {
      const response = await assessmentService.startAssessment(assessmentId);
      setAssessment(prev => ({ ...prev, status: 'in_progress' }));
      
      // Set up timer if there's a time limit
      if (response.time_remaining) {
        setTimeRemaining(response.time_remaining);
        startTimer(response.time_remaining);
      }
      
      loadCurrentQuestion();
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const startTimer = (seconds) => {
    setTimeRemaining(seconds);
    
    timerIntervalRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timerIntervalRef.current);
          completeAssessment();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };
  
  const formatTimeRemaining = (seconds) => {
    if (!seconds) return '--:--';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  const loadCurrentQuestion = async () => {
    setIsLoading(true);
    try {
      const response = await assessmentService.getCurrentQuestion(assessmentId);
      
      if ('message' in response && response.message.includes('completed')) {
        await completeAssessment();
        return;
      }
      
      setCurrentQuestion(response.question);
      setProgress({
        current: response.questions_answered,
        total: response.total_questions
      });
      
      // Reset answer state for new question
      setAnswer('');
      
      // For typing questions, initialize typing metrics
      if (response.question.specialization === 'typing') {
        typingStartTimeRef.current = null;
        typingCharactersRef.current = 0;
        typingErrorsRef.current = 0;
      }
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleTypingInput = (e) => {
    const typedText = e.target.value;
    setAnswer(typedText);
    
    // Initialize start time on first input
    if (typingStartTimeRef.current === null && typedText.length > 0) {
      typingStartTimeRef.current = Date.now();
    }
    
    // Count characters and errors
    typingCharactersRef.current = typedText.length;
    
    if (currentQuestion) {
      const correctText = currentQuestion.content;
      let errors = 0;
      
      for (let i = 0; i < typedText.length && i < correctText.length; i++) {
        if (typedText[i] !== correctText[i]) {
          errors++;
        }
      }
      
      // Add errors for missing or extra characters
      errors += Math.abs(correctText.length - typedText.length);
      typingErrorsRef.current = errors;
    }
  };
  
  const calculateTypingMetrics = () => {
    if (!typingStartTimeRef.current) return null;
    
    const endTime = Date.now();
    const timeMs = endTime - typingStartTimeRef.current;
    const minutes = timeMs / 60000;
    
    // Typing speed in characters per minute
    const charsPerMinute = typingCharactersRef.current / minutes;
    
    // Words per minute (standard 5 chars = 1 word)
    const wpm = charsPerMinute / 5;
    
    // Accuracy as percentage
    const correctChars = typingCharactersRef.current - typingErrorsRef.current;
    const accuracy = correctChars > 0 
      ? Math.max(0, Math.min(100, (correctChars / typingCharactersRef.current) * 100))
      : 0;
    
    return {
      wpm: Math.round(wpm),
      accuracy: Math.round(accuracy),
      time_ms: timeMs,
      characters: typingCharactersRef.current,
      errors: typingErrorsRef.current
    };
  };
  
  const submitAnswer = async () => {
    if (!answer.trim() && currentQuestion?.specialization !== 'typing') {
      toast.error('Please provide an answer');
      return;
    }
    
    setIsSubmitting(true);
    try {
      let typingMetrics = null;
      
      if (currentQuestion.specialization === 'typing') {
        typingMetrics = calculateTypingMetrics();
      }
      
      await assessmentService.submitAnswer(
        assessmentId,
        currentQuestion.id,
        answer,
        typingMetrics
      );
      
      loadCurrentQuestion();
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const completeAssessment = async () => {
    setIsSubmitting(true);
    try {
      await assessmentService.completeAssessment(assessmentId);
      
      toast.success('Assessment completed!');
      navigate(`/assessment/results/${assessmentId}?email=${email}&token=${token}`);
    } catch (error) {
      handleError(error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (isLoading && !assessment) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-vh-100 bg-light py-4">
      <div className="container">
        <div className="card shadow-sm">
          <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center">
            <h5 className="mb-0">{assessment?.template_name || 'Assessment'}</h5>
            {timeRemaining !== null && (
              <div className="badge bg-primary fs-6">
                <i className="bi bi-clock me-1"></i>
                {formatTimeRemaining(timeRemaining)}
              </div>
            )}
          </div>
          
          <div className="card-body p-4">
            {assessment?.status === 'pending' ? (
              <div className="text-center py-5">
                <h2 className="h4 mb-4">Ready to start your assessment?</h2>
                <p className="mb-4">
                  You are about to start an assessment: <strong>{assessment.template_name}</strong>
                </p>
                
                {assessment.time_limit && (
                  <div className="alert alert-info mb-4">
                    <i className="bi bi-info-circle me-2"></i>
                    This assessment has a time limit of <strong>{assessment.time_limit} minutes</strong>.
                    Once you start, the timer will begin.
                  </div>
                )}
                
                <Button
                  variant="primary"
                  size="lg"
                  onClick={startAssessment}
                  isLoading={isSubmitting}
                >
                  Start Assessment
                </Button>
              </div>
            ) : isLoading ? (
              <div className="d-flex justify-content-center p-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : currentQuestion ? (
              <div>
                {/* Progress indicator */}
                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>Question {progress.current + 1} of {progress.total}</span>
                    <span>{Math.round(((progress.current) / progress.total) * 100)}% Complete</span>
                  </div>
                  <div className="progress">
                    <div 
                      className="progress-bar" 
                      role="progressbar" 
                      style={{ width: `${((progress.current) / progress.total) * 100}%` }}
                      aria-valuenow={progress.current}
                      aria-valuemin="0"
                      aria-valuemax={progress.total}
                    ></div>
                  </div>
                </div>
                
                {/* Reading Comprehension Set */}
                {currentQuestion.reading_set && (
                  <div className="card mb-4">
                    <div className="card-body bg-light">
                      <h6 className="card-title">Reading Passage</h6>
                      <p className="card-text">{currentQuestion.reading_set.paragraph}</p>
                    </div>
                  </div>
                )}
                
                {/* Question Content */}
                <div className="mb-4">
                  <h5 className="mb-3">
                    {currentQuestion.specialization === 'typing' 
                      ? 'Type the following text:' 
                      : currentQuestion.content}
                  </h5>
                  
                  {currentQuestion.specialization === 'typing' && (
                    <div className="card mb-4">
                      <div className="card-body bg-light">
                        <p className="card-text font-monospace">{currentQuestion.content}</p>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Answer Input */}
                <div className="mb-4">
                  {currentQuestion.specialization === 'aptitude' && currentQuestion.options ? (
                    <div className="list-group">
                      {currentQuestion.options.map((option, index) => (
                        <label 
                          key={index} 
                          className={`list-group-item list-group-item-action ${answer === option ? 'active' : ''}`}
                        >
                          <input
                            type="radio"
                            name="questionOption"
                            value={option}
                            checked={answer === option}
                            onChange={(e) => setAnswer(e.target.value)}
                            className="me-2"
                          />
                          {option}
                        </label>
                      ))}
                    </div>
                  ) : currentQuestion.specialization === 'typing' ? (
                    <div className="form-group">
                      <label className="form-label">Type here:</label>
                      <textarea
                        className="form-control font-monospace"
                        rows="5"
                        value={answer}
                        onChange={handleTypingInput}
                        placeholder="Start typing..."
                      ></textarea>
                    </div>
                  ) : (
                    <div className="form-group">
                      <label className="form-label">Your Answer:</label>
                      <textarea
                        className="form-control"
                        rows="3"
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Enter your answer..."
                      ></textarea>
                    </div>
                  )}
                </div>
                
                <div className="d-flex justify-content-end">
                  <Button
                    variant="primary"
                    onClick={submitAnswer}
                    isLoading={isSubmitting}
                  >
                    Submit Answer
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-5">
                <h3>Loading next question...</h3>
                <div className="spinner-border text-primary mt-3" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TakeAssessment;
