import React, { useState, useEffect } from 'react';
import { authService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { AuthContext } from './auth-context';

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return;
        }

        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to load user:', error);
          if (error.response?.status === 401) {
            localStorage.removeItem('token');
            setUser(null);
          }
        }
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (credentials) => {
    try {
      const responseData = await authService.login(credentials);
      if (responseData.access_token) {
        localStorage.setItem('token', responseData.access_token);
        const userData = await authService.getCurrentUser();
        setUser(userData);
        toast.success('Login successful!');
        navigate('/dashboard');
        return true;
      }
      return false;
    } catch (error) {
      const errorMessage = error.response?.status === 401 
        ? 'Invalid email or password'
        : error.response?.data?.error || 'Login failed. Please try again.';
      
      toast.error(errorMessage);
      console.error('Login error details:', error);
      return false;
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        const userData = await authService.getCurrentUser();
        setUser(userData);
        toast.success('Registration successful! Please verify your email.');
        navigate('/dashboard');
      } else {
        toast.success('Registration successful! Please verify your email.');
        navigate('/login');
      }
      return true;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Registration failed');
      return false;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    navigate('/login');
    toast.success('Logged out successfully');
  };

  const updateProfile = async (userData) => {
    try {
      const responseData = await authService.updateProfile(userData);
      setUser(responseData.user);
      toast.success('Profile updated successfully');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update profile');
      return false;
    }
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        loading, 
        login, 
        register, 
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
