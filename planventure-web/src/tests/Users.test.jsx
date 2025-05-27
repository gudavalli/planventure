import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, beforeEach, expect } from 'vitest';
import AuthTestProvider from '../test-utils/AuthTestProvider';
import Users from '../pages/Users';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

// Mock react-hot-toast
vi.mock('react-hot-toast');

// Mock api service
vi.mock('../services/api', () => ({
  authService: {
    getAllUsers: vi.fn(),
    getRoles: vi.fn(),
    updateUserRole: vi.fn(),
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

describe('Users Component', () => {  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Setup default mock responses
    authService.getAllUsers.mockResolvedValue({ users: mockUsers });
    authService.getRoles.mockResolvedValue({ roles: mockRoles });
  });
    it('renders users table with correct data', async () => {
    render(
      <MemoryRouter>
        <AuthTestProvider>
          <Users />
        </AuthTestProvider>
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
    // Use getAllByText for "Talent Lead" since it appears in both the name cell and dropdown options
    const talentLeadElements = screen.getAllByText('Talent Lead');
    expect(talentLeadElements.length).toBeGreaterThan(0);
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
  });  it('allows role changes for users', async () => {
    authService.updateUserRole.mockResolvedValue({
      message: 'User role updated successfully',
      user: { ...mockUsers[2], role: 'TALENT_LEAD' },
    });

    // Mock window.confirm to return true
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <MemoryRouter>
        <AuthTestProvider>
          <Users />
        </AuthTestProvider>
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

    // Verify confirm was called
    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalledWith("Are you sure you want to change this user's role to TALENT_LEAD?");
    });

    // Verify API call
    await waitFor(() => {
      expect(authService.updateUserRole).toHaveBeenCalledWith(3, 'TALENT_LEAD');
    });

    // Verify success toast
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('User role updated successfully');
    });    // Clean up
    confirmSpy.mockRestore();
  });  it('handles errors when loading users', async () => {
    // Mock API error
    authService.getAllUsers.mockRejectedValue(new Error('Failed to load users'));

    render(
      <MemoryRouter>
        <AuthTestProvider>
          <Users />
        </AuthTestProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Unable to connect to the server. Please try again later.');
    });
  });
  it('handles errors when updating user role', async () => {
    // Load users successfully
    authService.getAllUsers.mockResolvedValue({ users: mockUsers });
    
    // Mock update error
    authService.updateUserRole.mockRejectedValue(new Error('Failed to update role'));
    
    // Mock window.confirm to return true
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
      render(
      <MemoryRouter>
        <AuthTestProvider>
          <Users />
        </AuthTestProvider>
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
      expect(toast.error).toHaveBeenCalledWith('Unable to connect to the server. Please try again later.');
    });
    
    // Clean up
    confirmSpy.mockRestore();
  });
});
