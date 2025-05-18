import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/api';
import Button from '../components/Button';
import Input from '../components/Input';
import FormError from '../components/FormError';
import toast from 'react-hot-toast';

const ForgotPassword = () => {  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [resetError, setResetError] = useState('');
  const [emailError, setEmailError] = useState('');
  const validateEmail = () => {
    if (!email) {
      setEmailError('Email is required');
      return false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setEmailError('Please enter a valid email address');
      return false;
    }
    setEmailError('');
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateEmail()) return;

    setResetError('');
    setIsLoading(true);
    try {
      await authService.forgotPassword(email);
      setEmailSent(true);
      toast.success('Password reset instructions sent to your email');
    } catch (error) {
      // Handle different types of errors
      if (!navigator.onLine) {
        setResetError('Network connection error. Please check your internet connection.');
      } else if (error.message === 'Network Error') {
        setResetError('Unable to connect to the server. Please try again later.');
      } else {
        setResetError(error.response?.data?.error || 'Failed to send reset email. Please try again.');
      }
      toast.error('Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };
  if (emailSent) {
    return (
      <div className="container py-5 d-flex align-items-center justify-content-center min-vh-100">
        <div className="col-md-6 col-lg-4 text-center">
          <div className="alert alert-success d-flex align-items-center" role="alert">
            <div className="me-3">
              <svg width="24" height="24" fill="currentColor" className="bi bi-check-circle-fill" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
              </svg>
            </div>
            <div className="text-start">
              <h5>Email sent</h5>
              <p className="mb-0">
                Check your email for password reset instructions.
              </p>
            </div>
          </div>
          <div className="mt-4">
            <Link to="/login" className="btn btn-link">
              Return to login
            </Link>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="container py-5 d-flex align-items-center justify-content-center min-vh-100">
      <div className="row justify-content-center w-100">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body p-4">              <div className="text-center mb-4">
                <h2 className="h4 mb-2">Reset your password</h2>
                <p className="text-muted small">
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>
              
              <FormError message={resetError} />
              
              <form onSubmit={handleSubmit}>                <Input
                  label="Email address"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setEmailError('');
                    setResetError('');
                  }}
                  error={emailError}
                />
                <Button
                  type="submit"
                  variant="primary"
                  className="w-100 mb-3"
                  isLoading={isLoading}
                >
                  Send reset link
                </Button>
                <div className="text-center">
                  <Link to="/login" className="btn btn-link">
                    Back to login
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
