import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, test, beforeEach, expect } from 'vitest';
import EditQuestion from '../EditQuestion';
import { assessmentService } from '../../../services/api';

// Mock the error handler
const mockHandleError = vi.fn();
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: mockHandleError
  })
}));

// Mock AuthContext
const mockAuthContext = {
  user: { id: 1, email: 'test@test.com' },
  loading: false,
  login: vi.fn(),
  logout: vi.fn()
};

vi.mock('../../../context/auth-hooks', () => ({
  useAuth: () => mockAuthContext
}));

// Mock the React Router hooks
const mockNavigate = vi.fn();
const mockParams = { questionId: '123' };

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockParams
  };
});

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    error: vi.fn(),
    success: vi.fn()
  }
}));

// Mock Navigation and Button components
vi.mock('../../Navigation', () => ({
  default: () => <nav>Navigation</nav>
}));

vi.mock('../../Button', () => ({
  default: ({ children, onClick, type, variant, isLoading, disabled }) => (
    <button 
      onClick={onClick} 
      type={type} 
      className={`btn ${variant}`}
      disabled={disabled || isLoading}
    >
      {children}
    </button>
  )
}));

vi.mock('../../Input', () => ({
  default: ({ value, onChange, ...props }) => (
    <input value={value} onChange={onChange} {...props} />
  )
}));

// Mock the assessment service
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getQuestionDetails: vi.fn(),
    updateQuestion: vi.fn()
  }
}));

describe('EditQuestion Component', () => {
  beforeEach(() => {
    // Setup mock data
    const mockQuestion = {
      id: '123',
      specialization: 'aptitude',
      content: 'Test question',
      options: ['Option 1', 'Option 2', 'Option 3'],
      correct_answer: 0,
      explanation: 'This is an explanation',
      difficulty: 'medium',
      time_limit: 60
    };
    
    // Reset mocks
    vi.clearAllMocks();
    
    // Mock the API response
    assessmentService.getQuestionDetails.mockResolvedValue(mockQuestion);
    assessmentService.updateQuestion.mockResolvedValue({ message: 'Question updated successfully' });
  });

  test('loads and displays question data', async () => {
    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(assessmentService.getQuestionDetails).toHaveBeenCalledWith('123');
    });
    
    // Check that form fields are populated with the mock data
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
      expect(screen.getByLabelText(/Time Limit/i).value).toBe('60');
    });
  });

  test('handles form submission correctly', async () => {
    const { container } = render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
    });
    
    // Modify a field
    const contentInput = screen.getByLabelText(/Question Content/i);
    fireEvent.change(contentInput, { target: { value: 'Updated question content' } });
    
    // Select a correct answer first (required for submission)
    const letterA = screen.getByTitle('Select option A as correct answer');
    fireEvent.click(letterA);
    
    // Find form with querySelector and submit it
    const form = container.querySelector('form');
    expect(form).toBeTruthy();
    
    fireEvent.submit(form);
    
    // Check that the updateQuestion API was called with the correct data
    await waitFor(() => {
      expect(assessmentService.updateQuestion).toHaveBeenCalledWith('123', expect.objectContaining({
        content: 'Updated question content',
        specialization: 'aptitude',
        options: ['Option 1', 'Option 2', 'Option 3'],
        correct_answer: 'Option 1'  // Should be option text, not index
      }));
    });
  });

  test('handles validation errors', async () => {
    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
    });
    
    // Clear the content field to trigger validation error
    const contentInput = screen.getByLabelText(/Question Content/i);
    fireEvent.change(contentInput, { target: { value: '' } });
    
    // Submit the form using form submission
    const form = contentInput.closest('form');
    fireEvent.submit(form);

    // Check that inline validation error is shown and API wasn't called
    await waitFor(() => {
      expect(contentInput).toHaveClass('is-invalid');
      expect(screen.getByText('Question content is required')).toBeInTheDocument();
      expect(assessmentService.updateQuestion).not.toHaveBeenCalled();
    });
  });

  test('handles API errors', async () => {
    // Mock API error
    const mockError = new Error('API Error');
    assessmentService.updateQuestion.mockRejectedValue(mockError);
    
    const { container } = render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
    });
    
    // Select a correct answer first (required for submission)
    const letterA = screen.getByTitle('Select option A as correct answer');
    fireEvent.click(letterA);
    
    // Submit the form using direct form submission
    const form = container.querySelector('form');
    expect(form).toBeTruthy();
    
    fireEvent.submit(form);
    
    // Check that error handler was called with the error
    await waitFor(() => {
      expect(assessmentService.updateQuestion).toHaveBeenCalled();
      expect(mockHandleError).toHaveBeenCalledWith(mockError);
    });
  });

  test('clickable option letters work correctly', async () => {
    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
    });
    
    // Find the option letter buttons (A, B, C) - using the shared component titles
    await waitFor(() => {
      expect(screen.getByTitle('Select option A as correct answer')).toBeInTheDocument();
    });
    
    const letterA = screen.getByTitle('Select option A as correct answer');
    const letterB = screen.getByTitle('Select option B as correct answer');
    const letterC = screen.getByTitle('Select option C as correct answer');
    
    // Initially, no letter should be selected since the form starts without a correct answer set
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-outline-secondary');
    expect(letterC).toHaveClass('btn-outline-secondary');
    
    // Click on letter A
    fireEvent.click(letterA);
    
    // Now letter A should be selected (btn-success)
    expect(letterA).toHaveClass('btn-success');
    expect(letterB).toHaveClass('btn-outline-secondary');
    expect(letterC).toHaveClass('btn-outline-secondary');
    
    // Click on letter B
    fireEvent.click(letterB);
    
    // Now letter B should be selected (btn-success) and A should be deselected
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-success');
    expect(letterC).toHaveClass('btn-outline-secondary');
    
    // Click on letter C
    fireEvent.click(letterC);
    
    // Now letter C should be selected (btn-success) and B should be deselected
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-outline-secondary');
    expect(letterC).toHaveClass('btn-success');
  });
});
