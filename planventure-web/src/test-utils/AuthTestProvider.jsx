import React from 'react';
import { vi } from 'vitest';
import { AuthContext } from '../context/auth-context';

const AuthTestProvider = ({ children, value = {} }) => {
  const defaultValue = {
    user: { 
      id: 1, 
      email: 'admin@test.com', 
      first_name: 'Admin', 
      last_name: 'User',
      role: 'admin' 
    },
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    updateProfile: vi.fn(),
    ...value
  };

  return (
    <AuthContext.Provider value={defaultValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthTestProvider;
