import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import renderer from 'react-test-renderer';
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
  success: vi.fn(),
  error: vi.fn(),
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

describe('TemplateDetails Snapshot Tests', () => {
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
  it('renders TemplateDetails correctly', async () => {
    const component = renderer.create(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );
    
    // Let the component load data
    await new Promise(resolve => setTimeout(resolve, 0));

    // Update the snapshot
    let tree = component.toJSON();
    expect(tree).toMatchSnapshot();
  });
    it('renders delete confirmation modal correctly', async () => {
    const { baseElement } = render(
      <BrowserRouter>
        <AuthTestProvider>
          <TemplateDetails />
        </AuthTestProvider>
      </BrowserRouter>
    );
    
    // Wait for data to load
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Get the modal element
    const modal = baseElement.querySelector('.modal');
    expect(modal).toMatchSnapshot();
  });
});
