import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { authService } from '../services/api';
import Button from '../components/Button';
import Input from '../components/Input';
import FormError from '../components/FormError';
import toast from 'react-hot-toast';

const ResetPassword = () => {
  const { token } = useParams();
  const navigate = useNavigate();  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [resetError, setResetError] = useState('');
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
    setResetError('');
  };
  const validate = () => {
    const newErrors = {};
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[0-9]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one number';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setResetError('');
    setIsLoading(true);
    try {
      await authService.resetPassword(token, formData.password);
      toast.success('Password reset successful');
      navigate('/login');
    } catch (error) {
      // Handle different types of errors
      if (!navigator.onLine) {
        setResetError('Network connection error. Please check your internet connection.');
      } else if (error.message === 'Network Error') {
        setResetError('Unable to connect to the server. Please try again later.');
      } else if (error.response?.status === 400) {
        setResetError('Invalid password reset token. Please request a new password reset link.');
      } else if (error.response?.status === 404) {
        setResetError('The password reset link has expired. Please request a new one.');
      } else {
        setResetError(error.response?.data?.error || 'Failed to reset password. Please try again.');
      }
      toast.error('Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="container py-5 d-flex align-items-center justify-content-center min-vh-100">
      <div className="row justify-content-center w-100">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body p-4">              <div className="text-center mb-4">
                <h2 className="h4 mb-2">Reset your password</h2>
                <p className="text-muted small">
                  Enter your new password below.
                </p>
              </div>
              
              <FormError message={resetError} />
              
              <form onSubmit={handleSubmit}>
                <Input
                  label="New Password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  error={errors.password}
                />
                <Input
                  label="Confirm New Password"
                  name="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  error={errors.confirmPassword}
                />
                <Button
                  type="submit"
                  variant="primary"
                  className="w-100 mt-3"
                  isLoading={isLoading}
                >
                  Reset Password
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
