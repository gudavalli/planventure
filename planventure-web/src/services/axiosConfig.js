import axios from 'axios';

const BASE_URL = '/api';  // Use relative URL to work with Vite proxy

export const createAxiosInstance = () => {
  const instance = axios.create({
    baseURL: BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true
  });

  // Add token to requests if it exists
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Handle response errors
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (!error.response) {
        return Promise.reject(new Error('Network error'));
      }
    if (error.response.status === 401) {
      // Only remove token and redirect if we're not already on the login page
      // and not trying to log in
      const isLoginRequest = error.config.url.endsWith('/auth/login');
      const isCurrentUserRequest = error.config.url.endsWith('/auth/me');
      if (!isLoginRequest && !isCurrentUserRequest) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }

      if (error.response.status === 403) {
        // Handle forbidden errors
        window.location.href = '/dashboard';
      }

      return Promise.reject(error);
    }
  );

  return instance;
};
