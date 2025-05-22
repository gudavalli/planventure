import { useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth-hooks';

export const useApiErrorHandler = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleError = useCallback((error) => {
    if (!error.response) {
      if (!navigator.onLine) {
        toast.error('Network connection error. Please check your internet connection.');
      } else {
        toast.error('Unable to connect to the server. Please try again later.');
      }
      return;
    }

    switch (error.response.status) {
      case 400:
        toast.error(error.response.data?.error || 'Invalid request. Please check your input.');
        break;
      case 401:
        toast.error('Session expired. Please log in again.');
        logout();
        break;
      case 403:
        toast.error('You do not have permission to perform this action.');
        navigate('/dashboard');
        break;
      case 404:
        toast.error('Resource not found.');
        break;
      case 429:
        toast.error('Too many requests. Please try again later.');
        break;
      case 500:
        toast.error('Server error. Please try again later.');
        break;
      default:
        toast.error(error.response.data?.error || 'An unexpected error occurred.');
    }
  }, [navigate, logout]);

  return { handleError };
};
