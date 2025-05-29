import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import AuthTestProvider from '../../../test-utils/AuthTestProvider';
import QuestionBankDashboard from '../QuestionBankDashboard';
import { assessmentService } from '../../../services/api';

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock api service
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getQuestions: vi.fn(),
    deleteQuestion: vi.fn(),
  },
}));

// Mock useApiErrorHandler hook
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn(),
  }),
}));

const mockQuestionsResponse = {
  questions: [
    {
      id: 1,
      content: 'What is 2+2?',
      options: ['3', '4', '5', '6'],
      correct_answer: 4,
      specialization: 'aptitude',
      difficulty: 'easy',
      time_limit: 60,
    },
    {
      id: 2,
      content: 'What is the capital of France?',
      options: ['London', 'Berlin', 'Paris', 'Madrid'],
      correct_answer: 'Paris',
      specialization: 'technical',
      difficulty: 'medium',
      time_limit: 60,
    },
  ],
  pagination: {
    total_items: 2,
    total_pages: 1,
    current_page: 1,
    per_page: 10,
    has_next: false,
    has_prev: false,
    next_page: null,
    prev_page: null,
  },
};

const renderComponent = () => {
  return render(
    <AuthTestProvider>
      <MemoryRouter>
        <QuestionBankDashboard />
      </MemoryRouter>
    </AuthTestProvider>
  );
};

describe('QuestionBankDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assessmentService.getQuestions.mockResolvedValue(mockQuestionsResponse);
  });

  describe('Initial Rendering', () => {    it('renders the dashboard with correct header', async () => {
      renderComponent();

      expect(screen.getByRole('heading', { name: 'Question Bank' })).toBeInTheDocument();
      expect(screen.getByText('Manage your assessment questions independently')).toBeInTheDocument();
    });

    it('calls getQuestions API on initial load', async () => {
      renderComponent();

      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'all', '', '', ''
        );
      });
    });

    it('displays questions when loaded', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
        expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    it('triggers search when typing in search box', async () => {
      renderComponent();

      const searchInput = screen.getByRole('textbox');
      
      fireEvent.change(searchInput, { target: { value: 'capital' } });

      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'all', 'capital', '', ''
        );
      });
    });
  });

  describe('Filter Functionality', () => {
    it('applies specialization filter', async () => {
      renderComponent();

      const specializationSelect = screen.getByDisplayValue('All Specializations');
      
      fireEvent.change(specializationSelect, { target: { value: 'aptitude' } });

      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'all', '', 'aptitude', ''
        );
      });
    });

    it('applies difficulty filter', async () => {
      renderComponent();

      const difficultySelect = screen.getByDisplayValue('All Difficulties');
      
      fireEvent.change(difficultySelect, { target: { value: 'easy' } });

      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'all', '', '', 'easy'
        );
      });
    });

    it('applies question type filter', async () => {
      renderComponent();

      const typeSelect = screen.getByDisplayValue('All Types');
      
      fireEvent.change(typeSelect, { target: { value: 'aptitude' } });

      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'aptitude', '', '', ''
        );
      });
    });
  });

  describe('Reset Functionality', () => {
    it('resets all filters and search when reset button is clicked', async () => {
      renderComponent();

      // Set some filters
      const searchInput = screen.getByRole('textbox');
      const resetButton = screen.getByRole('button', { name: /reset/i });

      fireEvent.change(searchInput, { target: { value: 'test' } });

      // Click reset
      fireEvent.click(resetButton);

      // Verify search is cleared
      expect(searchInput.value).toBe('');

      // Verify API is called with cleared filters
      await waitFor(() => {
        expect(assessmentService.getQuestions).toHaveBeenCalledWith(
          1, 10, 'all', '', '', ''
        );
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading spinner initially', () => {
      renderComponent();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('hides loading spinner after data loads', async () => {
      renderComponent();

      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      const mockError = new Error('API Error');
      assessmentService.getQuestions.mockRejectedValue(mockError);

      renderComponent();      // The component should still render without crashing
      expect(screen.getByRole('heading', { name: 'Question Bank' })).toBeInTheDocument();
    });
  });
});
