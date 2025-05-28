import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import AuthTestProvider from '../../../test-utils/AuthTestProvider';
import ViewQuestionDetails from '../ViewQuestionDetails';
import { assessmentService } from '../../../services/api';

// Mock react-router-dom
const mockUseParams = vi.fn();
const mockUseLocation = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => mockUseParams(),
    useLocation: () => mockUseLocation(),
  };
});

// Mock assessmentService
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getQuestionDetails: vi.fn(),
  },
}));

// Mock the hooks
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn(),
  }),
}));

describe('ViewQuestionDetails Navigation Fixes', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Setup default mock responses
    mockUseParams.mockReturnValue({ questionId: '123' });
    assessmentService.getQuestionDetails.mockResolvedValue({
      id: 123,
      content: 'What is the capital of France?',
      specialization: 'aptitude',
      options: ['London', 'Paris', 'Berlin', 'Madrid'],
      correct_answer: 'Paris',
      explanation: 'Paris is the capital city of France.',
      difficulty: 'medium',
      time_limit: 60,
    });
  });

  it('should pass a basic test', () => {
    expect(true).toBe(true);
  });

  it('should use referrer from location state for edit navigation', async () => {
    // Mock location with referrer state (our navigation fix)
    mockUseLocation.mockReturnValue({
      pathname: '/assessments/questions/123',
      state: { referrer: '/assessments/templates/456' },
    });

    await act(async () => {
      render(
        <BrowserRouter>
          <AuthTestProvider>
            <ViewQuestionDetails />
          </AuthTestProvider>
        </BrowserRouter>
      );
    });

    // Wait for question details to load
    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Verify the edit link includes the referrer parameter
    const editLink = screen.getByRole('link', { name: /edit/i });
    expect(editLink).toHaveAttribute('href', expect.stringContaining('referrer=%2Fassessments%2Ftemplates%2F456'));
  });

  it('should handle missing referrer state gracefully', async () => {
    // Mock location without referrer state
    mockUseLocation.mockReturnValue({
      pathname: '/assessments/questions/123',
      state: null,
    });

    await act(async () => {
      render(
        <BrowserRouter>
          <AuthTestProvider>
            <ViewQuestionDetails />
          </AuthTestProvider>
        </BrowserRouter>
      );
    });

    // Wait for question details to load
    await waitFor(() => {
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    });

    // Verify the edit link works without referrer (fallback behavior)
    const editLink = screen.getByRole('link', { name: /edit/i });
    expect(editLink).toHaveAttribute('href', expect.stringContaining('/edit'));
  });
});
