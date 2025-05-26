import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import EditQuestion from './EditQuestion';
import { assessmentService } from '../../services/api';

// Mock the React Router hooks
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useParams: () => ({ questionId: '123' })
  };
});

// Mock the assessment service
vi.mock('../../services/api', () => ({
  assessmentService: {
    getQuestionDetails: vi.fn(),
    updateQuestion: vi.fn()
  }
}));

// Mock the error handler
vi.mock('../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn()
  })
}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn()
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
    const navigate = vi.fn();
    vi.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(navigate);
    
    render(
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
    
    // Submit the form
    const saveButton = screen.getByText(/Save Changes/i);
    fireEvent.click(saveButton);
    
    // Check that the updateQuestion API was called with the correct data
    await waitFor(() => {
      expect(assessmentService.updateQuestion).toHaveBeenCalledWith('123', expect.objectContaining({
        content: 'Updated question content',
        specialization: 'aptitude',
        options: ['Option 1', 'Option 2', 'Option 3'],
        correct_answer: 0
      }));
    });
    
    // Check navigation after save
    await waitFor(() => {
      expect(navigate).toHaveBeenCalledWith('/assessments/questions');
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
    
    // Submit the form
    const saveButton = screen.getByText(/Save Changes/i);
    fireEvent.click(saveButton);
    
    // Check that error toast was shown and API wasn't called
    await waitFor(() => {
      expect(require('react-hot-toast').default.error).toHaveBeenCalledWith('Question content is required');
      expect(assessmentService.updateQuestion).not.toHaveBeenCalled();
    });
  });

  test('handles API errors', async () => {
    // Mock API error
    const mockError = new Error('API Error');
    assessmentService.updateQuestion.mockRejectedValue(mockError);
    
    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );
    
    // Wait for the data to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i).value).toBe('Test question');
    });
    
    // Submit the form
    const saveButton = screen.getByText(/Save Changes/i);
    fireEvent.click(saveButton);
    
    // Check that error handler was called with the error
    await waitFor(() => {
      expect(require('../../hooks/useApiErrorHandler').useApiErrorHandler().handleError)
        .toHaveBeenCalledWith(mockError);
    });
  });
});
