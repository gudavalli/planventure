import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Input from '../components/Input';
import FormError from '../components/FormError';

const Login = () => {  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  const { login } = useAuth();
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
    
    // Clear login error when user starts typing
    if (loginError) {
      setLoginError('');
    }
  };
  const validate = () => {
    const newErrors = {};
    if (!formData.email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Please enter a valid email address';
    
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoginError('');
    setIsLoading(true);
    try {
      const success = await login(formData);
      if (!success) {
        setLoginError('Invalid email or password. Please try again.');
      }
    } catch (error) {
      // Handle different types of errors
      if (!navigator.onLine) {
        setLoginError('Network connection error. Please check your internet connection.');
      } else if (error.message === 'Network Error') {
        setLoginError('Unable to connect to the server. Please try again later.');
      } else {
        setLoginError(error.response?.data?.error || 'An error occurred during sign in. Please try again.');
      }
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container py-5 d-flex flex-column align-items-center">
      <div className="row justify-content-center w-100">
        <div className="col-md-6 col-lg-4">
          <div className="card shadow-sm">
            <div className="card-body p-4">              <div className="text-center mb-4">
                <h2 className="h4 mb-2">Sign in to your account</h2>
                <p className="text-muted small">Enter your credentials to access your account</p>
              </div>              <FormError message={loginError} />
              
              <form onSubmit={handleSubmit}>
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
                  autoComplete="current-password"
                />

                <div className="d-flex justify-content-between mb-3">
                  <div className="form-check">
                    <input 
                      id="remember-me" 
                      name="remember-me" 
                      type="checkbox" 
                      className="form-check-input" 
                    />
                    <label htmlFor="remember-me" className="form-check-label">
                      Remember me
                    </label>
                  </div>
                  <Link to="/forgot-password" className="small">
                    Forgot password?
                  </Link>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-100"
                  isLoading={isLoading}
                >
                  Sign in
                </Button>
              </form>
              
              <div className="text-center mt-4">
                <p className="mb-0 text-muted">
                  Don't have an account?{' '}
                  <Link to="/register">Sign up</Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
