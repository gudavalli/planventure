import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import QuestionBankEditQuestion from '../QuestionBankEditQuestion';
import { assessmentService } from '../../../services/api';
import AuthTestProvider from '../../../test-utils/AuthTestProvider';

// Mock the services
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getQuestionDetails: vi.fn(),
    updateQuestion: vi.fn(),
  },
}));

vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock useParams and useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ questionId: '123' }),
    useNavigate: () => mockNavigate,
  };
});

// Mock useApiErrorHandler hook
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn(),
  }),
}));

// Mock QuestionForm component
vi.mock('../QuestionForm', () => ({
  default: ({ mode, questionId }) => (
    <div data-testid="question-form">
      <span>Mode: {mode}</span>
      {questionId && <span>Question ID: {questionId}</span>}
      <input defaultValue="Test question content" />
    </div>
  ),
}));

const mockQuestionData = {
  id: '123',
  content: 'Test question content',
  specialization: 'aptitude',
  options: ['Option A', 'Option B', 'Option C', 'Option D'],
  correct_answer: 'Option B',
  explanation: 'Test explanation',
  difficulty: 'medium',
  time_limit: 60
};

const renderComponent = () => {
  return render(
    <AuthTestProvider>
      <MemoryRouter>
        <QuestionBankEditQuestion />
      </MemoryRouter>
    </AuthTestProvider>
  );
};

describe('QuestionBankEditQuestion', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    assessmentService.getQuestionDetails.mockResolvedValue(mockQuestionData);
    assessmentService.updateQuestion.mockResolvedValue({});
  });  it('renders component correctly', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Edit Question' })).toBeInTheDocument();
    });

    // Check that QuestionForm is rendered with correct props
    expect(screen.getByTestId('question-form')).toBeInTheDocument();
    expect(screen.getByText('Mode: edit')).toBeInTheDocument();
    expect(screen.getByText('Question ID: 123')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test question content')).toBeInTheDocument();
  });
});
