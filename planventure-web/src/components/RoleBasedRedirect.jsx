import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/auth-hooks';

const RoleBasedRedirect = () => {
  const { user } = useAuth();

  // Redirect based on user role
  if (user?.role === 'admin') {
    return <Navigate to="/users" replace />;
  }

  // For all other roles, redirect to dashboard
  return <Navigate to="/dashboard" replace />;
};

export default RoleBasedRedirect;
