import { createAxiosInstance } from './axiosConfig';
import { assessmentService } from './assessmentApi';

const api = createAxiosInstance();

export { assessmentService };

export const authService = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },

  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token, password) => {
    const response = await api.post(`/auth/reset-password/${token}`, { password });
    return response.data;
  },

  verifyEmail: async (token) => {
    const response = await api.get(`/auth/verify-email/${token}`);
    return response.data;
  },  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/auth/profile', userData);
    return {
      user: response.data
    };
  },

  changePassword: async (passwords) => {
    const response = await api.post('/auth/change-password', passwords);
    return response.data;
  },

  getAllUsers: async () => {
    const response = await api.get('/auth/users');
    return response.data;
  },

  getRoles: async () => {
    const response = await api.get('/auth/roles');
    return response.data;
  },

  updateUserRole: async (userId, role) => {
    const response = await api.put(`/auth/users/${userId}/role`, { role });
    return response.data;
  },

  resetUserPassword: async (userId) => {
    const response = await api.post(`/auth/users/${userId}/reset-password`);
    return response.data;
  },
};
