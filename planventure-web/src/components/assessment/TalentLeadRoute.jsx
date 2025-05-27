import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/auth-hooks';

/**
 * Route component that restricts access to Admin and Talent Lead roles only
 */
const TalentLeadRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user || (user.role !== 'admin' && user.role !== 'talent_lead')) {
    return <Navigate to="/dashboard" state={{ from: location }} replace />;
  }

  return children;
};

export default TalentLeadRoute;
