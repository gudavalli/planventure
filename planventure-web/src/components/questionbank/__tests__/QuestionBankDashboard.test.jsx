import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import QuestionBankDashboard from '../QuestionBankDashboard';
import { assessmentService } from '../../../services/api';
import toast from 'react-hot-toast';

// Mock react-hot-toast
vi.mock('react-hot-toast');

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

// Mock the auth context
vi.mock('../../../context/auth-hooks', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'Test User' },
    isAuthenticated: true,
  }),
}));

// Mock Navigation component
vi.mock('../../Navigation', () => {
  return {
    default: () => <nav data-testid="navigation">Navigation</nav>,
  };
});

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
  },
};

const renderQuestionBankDashboard = () => {
  return render(
    <MemoryRouter>
      <QuestionBankDashboard />
    </MemoryRouter>
  );
};

describe('QuestionBankDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assessmentService.getQuestions.mockResolvedValue(mockQuestionsResponse);
  });

  it('renders the main components', async () => {
    renderQuestionBankDashboard();
    
    expect(screen.getByText('Question Bank')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search by content...')).toBeInTheDocument();
    expect(screen.getByLabelText('Specialization')).toBeInTheDocument();
    expect(screen.getByLabelText('Difficulty')).toBeInTheDocument();
    expect(screen.getByLabelText('Question Type')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
    });
  });

  it('handles search functionality', async () => {
    renderQuestionBankDashboard();
    
    const searchInput = screen.getByPlaceholderText('Search by content...');
    fireEvent.change(searchInput, { target: { value: 'capital' } });
    
    expect(searchInput.value).toBe('capital');
  });

  it('handles specialization filter', async () => {
    renderQuestionBankDashboard();
    
    const specializationSelect = screen.getByLabelText('Specialization');
    fireEvent.change(specializationSelect, { target: { value: 'technical' } });
    
    await waitFor(() => {
      expect(assessmentService.getQuestions).toHaveBeenCalledWith(
        1, 10, 'all', '', 'technical', ''
      );
    });
  });

  it('handles difficulty filter', async () => {
    renderQuestionBankDashboard();
    
    const difficultySelect = screen.getByLabelText('Difficulty');
    fireEvent.change(difficultySelect, { target: { value: 'hard' } });
    
    await waitFor(() => {
      expect(assessmentService.getQuestions).toHaveBeenCalledWith(
        1, 10, 'all', '', '', 'hard'
      );
    });
  });

  it('handles question type filter', async () => {
    renderQuestionBankDashboard();
    
    const questionTypeSelect = screen.getByLabelText('Question Type');
    fireEvent.change(questionTypeSelect, { target: { value: 'aptitude' } });
    
    await waitFor(() => {
      expect(assessmentService.getQuestions).toHaveBeenCalledWith(
        1, 10, 'aptitude', '', '', ''
      );
    });
  });

  it('handles reset functionality', async () => {
    renderQuestionBankDashboard();
    
    // Set some filters first
    const searchInput = screen.getByPlaceholderText('Search by content...');
    const specializationSelect = screen.getByLabelText('Specialization');
    
    fireEvent.change(searchInput, { target: { value: 'test' } });
    fireEvent.change(specializationSelect, { target: { value: 'technical' } });
    
    // Click reset button
    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);
    
    // Check that inputs are cleared
    expect(searchInput.value).toBe('');
    expect(specializationSelect.value).toBe('');
  });
  it('displays question data correctly', async () => {
    renderQuestionBankDashboard();
    
    await waitFor(() => {
      expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
      expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
      // Use getAllByText since there are multiple questions with the same option count
      const optionTexts = screen.getAllByText('Multiple choice (4 options)');
      expect(optionTexts).toHaveLength(2);
    });
  });

  it('shows empty state when no questions', async () => {
    assessmentService.getQuestions.mockResolvedValue({
      questions: [],
      pagination: { total_items: 0, total_pages: 1, current_page: 1, per_page: 10 }
    });
    
    renderQuestionBankDashboard();
    
    await waitFor(() => {
      expect(screen.getByText('No questions found')).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    assessmentService.getQuestions.mockImplementation(() => new Promise(() => {}));
    
    renderQuestionBankDashboard();
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('displays filter compatibility message', async () => {
    renderQuestionBankDashboard();
    
    const questionTypeSelect = screen.getByLabelText('Question Type');
    const specializationSelect = screen.getByLabelText('Specialization');
    
    fireEvent.change(questionTypeSelect, { target: { value: 'typing' } });
    fireEvent.change(specializationSelect, { target: { value: 'aptitude' } });
    
    await waitFor(() => {
      expect(screen.getByText(/Note: Typing questions are typically only found/)).toBeInTheDocument();
    });
  });
});