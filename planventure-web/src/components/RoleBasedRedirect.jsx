import React from 'react';
import { Navigate } from 'react-router-dom';

const RoleBasedRedirect = () => {
  // Redirect all users to dashboard as the landing page
  return <Navigate to="/dashboard" replace />;
};

export default RoleBasedRedirect;
