import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import Users from '../pages/Users';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

// Mock react-hot-toast
jest.mock('react-hot-toast');

// Mock api service
jest.mock('../services/api', () => ({
  authService: {
    getAllUsers: jest.fn(),
    getRoles: jest.fn(),
    updateUserRole: jest.fn(),
  },
}));

const mockUsers = [
  {
    id: 1,
    email: 'admin@test.com',
    first_name: 'Admin',
    last_name: 'User',
    role: 'ADMIN',
    email_verified: true,
  },
  {
    id: 2,
    email: 'talent@test.com',
    first_name: 'Talent',
    last_name: 'Lead',
    role: 'TALENT_LEAD',
    email_verified: true,
  },
  {
    id: 3,
    email: 'test@test.com',
    first_name: 'Test',
    last_name: 'User',
    role: 'CANDIDATE',
    email_verified: false,
  },
];

const mockRoles = [
  { name: 'Admin', value: 'ADMIN' },
  { name: 'Talent Lead', value: 'TALENT_LEAD' },
  { name: 'Candidate', value: 'CANDIDATE' },
];

describe('Users Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup default mock responses
    authService.getAllUsers.mockResolvedValue({ users: mockUsers });
    authService.getRoles.mockResolvedValue({ roles: mockRoles });
  });
  
  it('renders users table with correct data', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <Users />
        </AuthProvider>
      </MemoryRouter>
    );

    // Check loading state
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('Admin User')).toBeInTheDocument();
    });

    // Verify all users are displayed
    expect(screen.getByText('Admin User')).toBeInTheDocument();
    expect(screen.getByText('Talent Lead')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
    
    // Verify email addresses
    expect(screen.getByText('admin@test.com')).toBeInTheDocument();
    expect(screen.getByText('talent@test.com')).toBeInTheDocument();
    expect(screen.getByText('test@test.com')).toBeInTheDocument();
    
    // Verify status badges
    const verifiedBadges = screen.getAllByText('Verified');
    const unverifiedBadge = screen.getByText('Unverified');
    expect(verifiedBadges).toHaveLength(2);
    expect(unverifiedBadge).toBeInTheDocument();
  });

  it('allows role changes for users', async () => {
    authService.updateUserRole.mockResolvedValue({
      message: 'User role updated successfully',
      user: { ...mockUsers[2], role: 'TALENT_LEAD' },
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <Users />
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Find role select for Test User
    const selects = screen.getAllByRole('combobox');
    const testUserSelect = selects[2]; // Third user in the list

    // Change role
    fireEvent.change(testUserSelect, { target: { value: 'TALENT_LEAD' } });

    // Verify API call
    await waitFor(() => {
      expect(authService.updateUserRole).toHaveBeenCalledWith(3, 'TALENT_LEAD');
    });

    // Verify success toast
    expect(toast.success).toHaveBeenCalledWith('User role updated successfully');
  });

  it('handles errors when loading users', async () => {
    // Mock API error
    authService.getAllUsers.mockRejectedValue(new Error('Failed to load users'));

    render(
      <MemoryRouter>
        <AuthProvider>
          <Users />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to load users');
    });
  });

  it('handles errors when updating user role', async () => {
    // Load users successfully
    authService.getAllUsers.mockResolvedValue({ users: mockUsers });
    
    // Mock update error
    authService.updateUserRole.mockRejectedValue(new Error('Failed to update role'));

    render(
      <MemoryRouter>
        <AuthProvider>
          <Users />
        </AuthProvider>
      </MemoryRouter>
    );

    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });

    // Find role select for Test User
    const selects = screen.getAllByRole('combobox');
    const testUserSelect = selects[2];

    // Change role
    fireEvent.change(testUserSelect, { target: { value: 'TALENT_LEAD' } });

    // Verify error toast
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to update role');
    });
  });
});
