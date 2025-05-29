import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, test, beforeEach, expect } from 'vitest';
import CreateQuestion from '../CreateQuestion';

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

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
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

// Mock assessment service
vi.mock('../../../services/api', () => ({
  assessmentService: {
    createQuestion: vi.fn()
  }
}));

describe('CreateQuestion Clickable Letters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });  test('clickable option letters work correctly in CreateQuestion', async () => {
    render(
      <BrowserRouter>
        <CreateQuestion />
      </BrowserRouter>
    );    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create Question' })).toBeInTheDocument();
    });
      // Should be in Multiple Choice mode by default
    const selectElement = screen.getByRole('combobox', { name: /question type/i });
    expect(selectElement).toHaveValue('aptitude');
    expect(screen.getByText('Multiple Choice')).toBeInTheDocument();
    
    // Add some option text so the letter buttons appear
    const optionA = screen.getByPlaceholderText('Option A');
    const optionB = screen.getByPlaceholderText('Option B');
    const optionC = screen.getByPlaceholderText('Option C'); 
    const optionD = screen.getByPlaceholderText('Option D');
    
    fireEvent.change(optionA, { target: { value: 'Option A text' } });
    fireEvent.change(optionB, { target: { value: 'Option B text' } });
    fireEvent.change(optionC, { target: { value: 'Option C text' } });
    fireEvent.change(optionD, { target: { value: 'Option D text' } });
    
    // Now find the option letter buttons (A, B, C, D) - they use the shared component pattern
    await waitFor(() => {
      expect(screen.getByTitle('Select option A as correct answer')).toBeInTheDocument();
    });
    
    const letterA = screen.getByTitle('Select option A as correct answer');
    const letterB = screen.getByTitle('Select option B as correct answer');
    const letterC = screen.getByTitle('Select option C as correct answer');
    const letterD = screen.getByTitle('Select option D as correct answer');
    
    // Initially, no letter should be selected (all should be outline-secondary)
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-outline-secondary');
    expect(letterC).toHaveClass('btn-outline-secondary');
    expect(letterD).toHaveClass('btn-outline-secondary');
    
    // Click on letter B
    fireEvent.click(letterB);
    
    // Now letter B should be selected (green) and others should remain unselected
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-success');
    expect(letterC).toHaveClass('btn-outline-secondary');
    expect(letterD).toHaveClass('btn-outline-secondary');
    
    // Click on letter D
    fireEvent.click(letterD);
    
    // Now letter D should be selected (green) and B should be deselected
    expect(letterA).toHaveClass('btn-outline-secondary');
    expect(letterB).toHaveClass('btn-outline-secondary');
    expect(letterC).toHaveClass('btn-outline-secondary');
    expect(letterD).toHaveClass('btn-success');
    
    // Verify the letters display correctly
    expect(letterA).toHaveTextContent('A');
    expect(letterB).toHaveTextContent('B');
    expect(letterC).toHaveTextContent('C');
    expect(letterD).toHaveTextContent('D');
  });
  test('option placeholders use letters instead of numbers', async () => {
    render(
      <BrowserRouter>
        <CreateQuestion />
      </BrowserRouter>
    );
    
    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create Question' })).toBeInTheDocument();
    });
    
    // Check that option inputs use letter placeholders
    expect(screen.getByPlaceholderText('Option A')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Option B')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Option C')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Option D')).toBeInTheDocument();
  });  test('instructions text is displayed', async () => {
    render(
      <BrowserRouter>
        <CreateQuestion />
      </BrowserRouter>
    );
    
    // Wait for component to render
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create Question' })).toBeInTheDocument();
    });
    
    // Add some option text so the instruction text appears
    const optionA = screen.getByPlaceholderText('Option A');
    fireEvent.change(optionA, { target: { value: 'Option A text' } });
    
    // Check that the instruction text is displayed
    await waitFor(() => {
      expect(screen.getByText('Click on the letter (A, B, C, D) to mark the correct answer. The selected letter will turn green.')).toBeInTheDocument();
    });
  });
});
