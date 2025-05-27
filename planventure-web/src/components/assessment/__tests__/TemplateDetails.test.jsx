import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import toast from 'react-hot-toast';
import AuthTestProvider from '../../../test-utils/AuthTestProvider';
import TemplateDetails from '../TemplateDetails';
import { assessmentService } from '../../../services/api';

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ templateId: '1' }),
    useNavigate: () => vi.fn(),
  };
});

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock assessmentService
vi.mock('../../../services/api', () => ({
  assessmentService: {
    getTemplateDetails: vi.fn(),
    removeQuestionFromTemplate: vi.fn(),
    addQuestionsToTemplate: vi.fn(),
    cloneTemplate: vi.fn(),
  },
}));

// Mock the hooks
vi.mock('../../../hooks/useApiErrorHandler', () => ({
  useApiErrorHandler: () => ({
    handleError: vi.fn(),
  }),
}));

describe('TemplateDetails', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Setup default mock responses
    assessmentService.getTemplateDetails.mockResolvedValue({
      id: 1,
      name: 'Test Template',
      description: 'Test Description',
      time_limit: 60,
      percentage: 70,
      questions: [
        {
          id: 101,
          content: 'What is the capital of France?',
          specialization: 'aptitude',
          options: ['London', 'Paris', 'Berlin', 'Madrid'],
        },
        {
          id: 102,
          content: 'What is 2+2?',
          specialization: 'aptitude',
          options: ['3', '4', '5', '6'],
        },
      ],
    });
  });
  it('renders template details', async () => {
    render(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );

    // Wait for template details to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText(/60 min/)).toBeInTheDocument();
      expect(screen.getByText(/70%/)).toBeInTheDocument();
    });

    // Check if questions are displayed
    expect(screen.getByText('What is the capital of France?')).toBeInTheDocument();
    expect(screen.getByText('What is 2+2?')).toBeInTheDocument();
  });  it('removes a question from template when delete button is clicked', async () => {
    assessmentService.removeQuestionFromTemplate.mockResolvedValue({ success: true });

    render(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );

    // Wait for template details to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Find the delete button by looking for the trash icon
    const deleteButtons = screen.getAllByRole('button').filter(button => 
      button.querySelector('.bi-trash')
    );
    
    console.log('Found delete buttons:', deleteButtons.length);
    expect(deleteButtons.length).toBeGreaterThan(0);
    
    const deleteButton = deleteButtons[0];
    console.log('Delete button:', deleteButton.outerHTML);
    
    // Click the delete button for the first question
    await act(async () => {
      fireEvent.click(deleteButton);
    });

    // Check if modal appears immediately
    let modalTitle = screen.queryByText('Confirm Removal');
    console.log('Modal title after click:', modalTitle);
      // Wait for modal to appear
    await waitFor(() => {
      expect(screen.getByText('Confirm Removal')).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to remove this question from the template?/)).toBeInTheDocument();
    });    // Debug: Print all available text content to see what's rendered
    console.log('Available text after modal appears:', screen.getAllByText(/Remove/i).map(el => el.textContent));
    
    // Try to find the Remove Question button with more specific selectors
    let removeButton;
    try {
      removeButton = screen.getByText('Remove Question');
      console.log('Found "Remove Question" button via text');
    } catch (error) {
      console.log('Could not find "Remove Question" text, trying button role...');
      const buttons = screen.getAllByRole('button');
      console.log('All buttons:', buttons.map(b => ({ text: b.textContent, classes: b.className })));
      removeButton = buttons.find(btn => btn.textContent.includes('Remove'));
      if (!removeButton) {
        // Try to find button with role and specific classes
        removeButton = buttons.find(btn => btn.textContent.trim() === 'Remove Question');
      }
      if (!removeButton) {
        console.log('All button text contents:', buttons.map(b => `"${b.textContent}"`));
      }
    }    console.log('Remove button found:', removeButton ? removeButton.outerHTML : 'NOT FOUND');
    expect(removeButton).toBeTruthy();
    
    // Click the Remove Question button and wait for async operations
    await act(async () => {
      fireEvent.click(removeButton);
      // Give some time for the async operations to start
      await new Promise(resolve => setTimeout(resolve, 100));
    });    // Add some debug logging to see what's happening
    console.log('After clicking Remove Question button');
    console.log('removeQuestionFromTemplate call count:', assessmentService.removeQuestionFromTemplate.mock.calls.length);
    console.log('getTemplateDetails call count:', assessmentService.getTemplateDetails.mock.calls.length);
    console.log('toast.success call count:', toast.success.mock.calls.length);

    // Verify that the API was called with correct parameters
    await waitFor(() => {
      expect(assessmentService.removeQuestionFromTemplate).toHaveBeenCalledWith('1', 101);
      expect(assessmentService.getTemplateDetails).toHaveBeenCalledWith('1');
      expect(toast.success).toHaveBeenCalledWith('Question removed from template successfully');
    }, { timeout: 3000 });
  });

  it('handles API error when deleting a question', async () => {    // Mock API error
    const error = new Error('Failed to delete question');
    assessmentService.removeQuestionFromTemplate.mockRejectedValue(error);

    render(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );    // Wait for template details to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Find the delete button by looking for the trash icon
    const deleteButton = screen.getAllByRole('button').find(button => 
      button.querySelector('.bi-trash')
    );
    
    expect(deleteButton).toBeTruthy(); // Make sure we found the button
    
    // Click the delete button for the first question
    fireEvent.click(deleteButton);

    // Confirmation modal should appear
    expect(screen.getByText('Confirm Removal')).toBeInTheDocument();

    // Click the Remove Question button
    fireEvent.click(screen.getByText('Remove Question'));

    // Verify that the API was called but error handling happened
    await waitFor(() => {
      expect(assessmentService.removeQuestionFromTemplate).toHaveBeenCalledWith('1', 101);
      // Error should be handled by the useApiErrorHandler hook
    });
  });  it('cancels question deletion when Cancel button is clicked', async () => {
    render(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );

    // Wait for template details to load
    await waitFor(() => {
      expect(screen.getByText('Test Template')).toBeInTheDocument();
    });

    // Find the delete button by looking for the trash icon
    const deleteButton = screen.getAllByRole('button').find(button => 
      button.querySelector('.bi-trash')
    );
    
    expect(deleteButton).toBeTruthy(); // Make sure we found the button
    
    // Click the delete button for the first question
    fireEvent.click(deleteButton);

    // Confirmation modal should appear
    expect(screen.getByText('Confirm Removal')).toBeInTheDocument();

    // Click the Cancel button
    fireEvent.click(screen.getByText('Cancel'));

    // Verify that the modal is closed and API was not called
    await waitFor(() => {
      expect(screen.queryByText('Confirm Removal')).not.toBeInTheDocument();
      expect(assessmentService.removeQuestionFromTemplate).not.toHaveBeenCalled();
    });
  });
});
