import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const loadUser = async () => {
      try {
        if (localStorage.getItem('token')) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Failed to load user:', error);
        localStorage.removeItem('token');
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
        // Fetch user data after successful login
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
      await authService.register(userData);
      toast.success('Registration successful! Please verify your email.');
      navigate('/login');
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
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
