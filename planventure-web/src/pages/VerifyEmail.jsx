import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

const VerifyEmail = () => {
  const { token } = useParams();
  const [status, setStatus] = useState('verifying'); // verifying, success, error

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        await authService.verifyEmail(token);
        setStatus('success');
        toast.success('Email verified successfully');
      } catch (error) {
        setStatus('error');
        toast.error(error.response?.data?.error || 'Failed to verify email');
      }
    };

    verifyEmail();
  }, [token]);
  const renderContent = () => {
    switch (status) {
      case 'verifying':
        return (
          <div className="text-center">
            <div className="spinner-border text-primary mb-3" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <h3 className="h5 mb-0">
              Verifying your email...
            </h3>
          </div>
        );
      
      case 'success':
        return (
          <div className="text-center">
            <div className="d-flex justify-content-center mb-3">
              <div className="bg-success bg-opacity-10 p-3 rounded-circle">
                <svg width="24" height="24" fill="currentColor" className="bi bi-check-lg text-success" viewBox="0 0 16 16">
                  <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                </svg>
              </div>
            </div>
            <h3 className="h5 mb-2">
              Email verified successfully!
            </h3>
            <p className="text-muted mb-4">
              You can now sign in to your account.
            </p>
            <Link
              to="/login"
              className="btn btn-primary"
            >
              Sign in
            </Link>
          </div>
        );
      
      case 'error':
        return (
          <div className="text-center">
            <div className="d-flex justify-content-center mb-3">
              <div className="bg-danger bg-opacity-10 p-3 rounded-circle">
                <svg width="24" height="24" fill="currentColor" className="bi bi-x-lg text-danger" viewBox="0 0 16 16">
                  <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/>
                </svg>
              </div>
            </div>
            <h3 className="h5 mb-2">
              Verification failed
            </h3>
            <p className="text-muted mb-4">
              The verification link may have expired or is invalid.
            </p>
            <Link
              to="/login"
              className="btn btn-primary"
            >
              Return to login
            </Link>
          </div>
        );
    }
  };
  return (
    <div className="container py-5 d-flex align-items-center justify-content-center min-vh-100">
      <div className="row justify-content-center w-100">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body p-4">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;
