import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../components/Navigation';
import Button from '../components/Button';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

import { useApiErrorHandler } from '../hooks/useApiErrorHandler';
import { debounce } from '../utils/apiUtils';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingUserIds, setUpdatingUserIds] = useState(new Set());  const { handleError } = useApiErrorHandler();

  const loadRoles = useCallback(async () => {
    try {
      const response = await authService.getRoles();
      setRoles(response.roles);
    } catch (error) {
      handleError(error);
    }
  }, [handleError]);

  const loadUsers = useCallback(async () => {
    try {
      const data = await authService.getAllUsers();
      setUsers(data.users);
    } catch (error) {
      handleError(error);
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const initializeData = async () => {
      try {
        await Promise.all([
          loadUsers(),
          loadRoles()
        ]);
      } catch (error) {
        if (isMounted) {
          handleError(error);
        }
      }
    };

    initializeData();

    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [loadUsers, loadRoles, handleError]);
  const debouncedLoadUsers = useCallback(() => {
    debounce(() => loadUsers(), 1000)();
  }, [loadUsers]);

  const handleRoleChange = async (userId, newRole) => {
    setUpdatingUserIds(prev => new Set([...prev, userId]));
    try {
      if (!window.confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
        return;
      }
      await authService.updateUserRole(userId, newRole);
      toast.success('User role updated successfully');
      debouncedLoadUsers();
    } catch (error) {
      handleError(error);
    } finally {
      setUpdatingUserIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  const handleResetPassword = async (userId) => {
    setUpdatingUserIds(prev => new Set([...prev, userId]));
    try {
      if (!window.confirm('Are you sure you want to reset this user\'s password?')) {
        return;
      }
      await authService.resetUserPassword(userId);
      toast.success('Password reset email sent successfully');
    } catch (error) {
      handleError(error);
    } finally {
      setUpdatingUserIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      <main className="container py-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="h3 mb-0">User Management</h1>
        </div>

        <div className="card shadow-sm">
          <div className="card-body">
            <div className="table-responsive">
              <table className="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>
                        {user.first_name} {user.last_name}
                      </td>
                      <td>{user.email}</td>
                      <td>
                        <select
                          className="form-select form-select-sm"
                          value={user.role}
                          onChange={(e) => handleRoleChange(user.id, e.target.value)}
                          disabled={updatingUserIds.has(user.id)}
                        >
                          {roles.map(role => (
                            <option key={role.value} value={role.value}>
                              {role.name}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span className={`badge ${user.email_verified ? 'bg-success' : 'bg-warning'}`}>
                          {user.email_verified ? 'Verified' : 'Unverified'}
                        </span>
                      </td>
                      <td>
                        <Button
                          variant="outline"
                          size="sm"
                          className="me-2"
                          disabled={updatingUserIds.has(user.id)}
                          onClick={() => handleResetPassword(user.id)}
                        >
                          Reset Password
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Users;
