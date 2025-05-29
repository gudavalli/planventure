import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import EditQuestion from '../EditQuestion';
import { assessmentService } from '../../../services/api';

// Mock the navigation functions
const mockNavigate = vi.fn();
const mockUseParams = vi.fn();
const mockUseLocation = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockUseParams(),
    useLocation: () => mockUseLocation(),
  };
});

// Mock the API service
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getQuestionDetails: vi.fn(),
    updateQuestion: vi.fn(),
  },
}));

// Mock the error handler
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn(),
  }),
}));

// Mock Navigation component
vi.mock('../../Navigation', () => ({
  default: () => '<nav>Navigation</nav>',
}));

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock Button component
vi.mock('../../Button', () => ({
  default: ({ children, onClick, type, className, isLoading, disabled }) => (
    <button 
      onClick={onClick} 
      type={type} 
      className={className} 
      disabled={disabled || isLoading}
    >
      {children}
    </button>
  ),
}));

describe('EditQuestion Cancel Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mocks
    mockUseParams.mockReturnValue({ questionId: '123' });
    
    // Mock successful API response
    assessmentService.getQuestionDetails.mockResolvedValue({
      id: 123,
      content: 'Test question',
      specialization: 'aptitude',
      options: ['Option 1', 'Option 2', 'Option 3'],
      correct_answer: 'Option 1',
      explanation: 'Test explanation',
      difficulty: 'medium',
      time_limit: 60,
    });
  });

  it('should always navigate to ViewQuestionDetails on cancel, regardless of returnTo parameter', async () => {
    // Mock location to simulate coming from template with returnTo parameter pointing to template
    mockUseLocation.mockReturnValue({
      search: '?returnTo=%2Fassessments%2Ftemplates%2F1',
      pathname: '/assessments/questions/123/edit',
    });

    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i)).toBeInTheDocument();
    });

    // Click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);    // Verify navigation goes to ViewQuestionDetails, NOT to the returnTo template path
    expect(mockNavigate).toHaveBeenCalledWith('/question-bank/123');
  });

  it('should navigate to ViewQuestionDetails when no returnTo parameter', async () => {
    // Mock location without returnTo parameter
    mockUseLocation.mockReturnValue({
      search: '',
      pathname: '/assessments/questions/123/edit',
    });

    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i)).toBeInTheDocument();
    });

    // Click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);    // Verify navigation to ViewQuestionDetails page
    expect(mockNavigate).toHaveBeenCalledWith('/question-bank/123');
  });

  it('should fix the original navigation issue: Template → View → Edit → Cancel should go to View', async () => {
    // This test simulates the exact issue described in the task:
    // User follows: Assessment template → view question → edit question → cancel → back
    // Previously went to Assessment management page, should now go to view question page
    
    mockUseLocation.mockReturnValue({
      search: '?returnTo=%2Fassessments%2Ftemplates%2F1', // This comes from template
      pathname: '/assessments/questions/123/edit',
    });

    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i)).toBeInTheDocument();
    });

    // Click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);    // FIXED: Cancel now goes back to ViewQuestionDetails instead of directly to template
    expect(mockNavigate).toHaveBeenCalledWith('/question-bank/123');
    
    // The returnTo parameter should still be available for the save operation (not tested here)
    // but cancel operation should ignore it and use cancelNavigationPath
  });

  it('should maintain consistent cancel behavior with different question IDs', async () => {
    // Test with different question ID to ensure the cancelNavigationPath is dynamic
    mockUseParams.mockReturnValue({ questionId: '456' });
    
    mockUseLocation.mockReturnValue({
      search: '?returnTo=%2Fassessments%2Ftemplates%2F2',
      pathname: '/assessments/questions/456/edit',
    });

    render(
      <BrowserRouter>
        <EditQuestion />
      </BrowserRouter>
    );

    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByLabelText(/Question Content/i)).toBeInTheDocument();
    });

    // Click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);    // Should navigate to the correct ViewQuestionDetails page for this question
    expect(mockNavigate).toHaveBeenCalledWith('/question-bank/456');
  });
});
