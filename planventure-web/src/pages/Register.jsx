import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/auth-hooks';
import Button from '../components/Button';
import Input from '../components/Input';
import FormError from '../components/FormError';

const Register = () => {  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [registerError, setRegisterError] = useState('');
  const { register } = useAuth();
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
    
    // Clear registration error when user starts typing
    if (registerError) {
      setRegisterError('');
    }
  };
  const validate = () => {
    const newErrors = {};    if (!formData.first_name) newErrors.first_name = 'First name is required';
    if (!formData.last_name) newErrors.last_name = 'Last name is required';
    
    if (!formData.email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Please enter a valid email address';
    
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    else if (!/[A-Z]/.test(formData.password)) newErrors.password = 'Password must contain at least one uppercase letter';
    else if (!/[0-9]/.test(formData.password)) newErrors.password = 'Password must contain at least one number';
    
    if (!formData.confirmPassword) newErrors.confirmPassword = 'Please confirm your password';
    else if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setRegisterError('');
    setIsLoading(true);
    try {
      const success = await register(formData);
      if (!success) {
        setRegisterError('Registration failed. Please try again.');
      }
    } catch (error) {
      // Handle different types of errors
      if (!navigator.onLine) {
        setRegisterError('Network connection error. Please check your internet connection.');
      } else if (error.message === 'Network Error') {
        setRegisterError('Unable to connect to the server. Please try again later.');
      } else if (error.response?.data?.error?.includes('already exists')) {
        setRegisterError('An account with this email already exists. Please try logging in instead.');
      } else {
        setRegisterError(error.response?.data?.error || 'An error occurred during registration. Please try again.');
      }
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container py-5 d-flex flex-column align-items-center">
      <div className="row justify-content-center w-100">
        <div className="col-md-8 col-lg-6">
          <div className="card shadow-sm">
            <div className="card-body p-4">              <div className="text-center mb-4">
                <h2 className="h4 mb-2">Create your account</h2>
                <p className="text-muted small">Fill out the form to get started</p>
              </div>
                <FormError message={registerError} />
              
              <form onSubmit={handleSubmit}>
                <div className="row g-3">
                  <div className="col-md-6">
                    <Input
                      label="First Name"                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      error={errors.first_name}
                      autoComplete="given-name"
                    />
                  </div>
                  
                  <div className="col-md-6">
                    <Input
                      label="Last Name"                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      error={errors.last_name}
                      autoComplete="family-name"
                    />
                  </div>
                </div>

                <Input
                  label="Email Address"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={errors.email}
                  autoComplete="email"
                  placeholder="name@example.com"
                />

                <Input
                  label="Password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  error={errors.password}
                  autoComplete="new-password"
                />
                
                <Input
                  label="Confirm Password"
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  error={errors.confirmPassword}
                  autoComplete="new-password"
                />

                <div className="form-check mb-3">
                  <input 
                    id="agree-terms" 
                    name="agreeTerms" 
                    type="checkbox" 
                    className="form-check-input" 
                    required 
                  />
                  <label htmlFor="agree-terms" className="form-check-label">
                    I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                  </label>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-100"
                  isLoading={isLoading}
                >
                  Sign up
                </Button>
              </form>
              
              <div className="text-center mt-4">
                <p className="mb-0 text-muted">
                  Already have an account?{' '}
                  <Link to="/login">Sign in</Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
