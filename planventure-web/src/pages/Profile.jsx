import { useState, useEffect } from 'react';
import Navigation from '../components/Navigation';
import Button from '../components/Button';
import Input from '../components/Input';
import { useAuth } from '../context/auth-hooks';
import { authService } from '../services/api';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
      });
    }
  }, [user]);

  const [isLoading, setIsLoading] = useState(false);
  const [contentLoading, setContentLoading] = useState(true);
  
  useEffect(() => {
    if (user) {
      setContentLoading(false);
    }
  }, [user]);

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [passwordErrors, setPasswordErrors] = useState({});

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
    setPasswordErrors(prev => ({ ...prev, [name]: '' }));
  };
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await updateProfile(formData);
      toast.success('Profile updated successfully');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update profile');
      console.error('Profile update error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const validatePasswordChange = () => {
    const errors = {};
    if (!passwordData.currentPassword) {
      errors.currentPassword = 'Current password is required';
    }
    if (!passwordData.newPassword) {
      errors.newPassword = 'New password is required';
    }
    if (passwordData.newPassword.length < 8) {
      errors.newPassword = 'Password must be at least 8 characters';
    }
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (!validatePasswordChange()) return;

    setIsLoading(true);
    try {
      await authService.changePassword(passwordData);
      toast.success('Password changed successfully');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to change password');
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        {contentLoading ? (
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : (
          <div className="row justify-content-center">
            <div className="col-lg-10">
              <div className="mb-4">
                <div className="card shadow-sm mb-4">
                  <div className="card-header bg-white py-3">
                    <h5 className="mb-0">Profile Information</h5>
                  </div>
                  <div className="card-body p-4">
                    <div className="row">
                      <div className="col-md-4 mb-4 mb-md-0">
                        <h6>Personal Information</h6>
                        <p className="text-muted small">
                          Update your personal information.
                        </p>
                      </div>
                      <div className="col-md-8">
                        <form onSubmit={handleProfileSubmit}>
                          <div className="row">
                            <div className="col-md-6">
                              <Input
                                label="First Name"
                                name="first_name"
                                type="text"
                                value={formData.first_name}
                                onChange={handleProfileChange}
                              />
                            </div>
                            <div className="col-md-6">
                              <Input
                                label="Last Name"
                                name="last_name"
                                type="text"
                                value={formData.last_name}
                                onChange={handleProfileChange}
                              />
                            </div>
                            <div className="col-md-6">
                              <Input
                                label="Phone Number"
                                name="phone"
                                type="tel"
                                value={formData.phone}
                                onChange={handleProfileChange}
                              />
                            </div>
                          </div>
                          <div className="d-flex justify-content-end">
                            <Button
                              type="submit"
                              isLoading={isLoading}
                            >
                              Save Changes
                            </Button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card shadow-sm">
                  <div className="card-header bg-white py-3">
                    <h5 className="mb-0">Security</h5>
                  </div>
                  <div className="card-body p-4">
                    <div className="row">
                      <div className="col-md-4 mb-4 mb-md-0">
                        <h6>Password</h6>
                        <p className="text-muted small">
                          Update your password.
                        </p>
                      </div>
                      <div className="col-md-8">
                        <form onSubmit={handlePasswordSubmit}>
                          <Input
                            label="Current Password"
                            name="currentPassword"
                            type="password"
                            value={passwordData.currentPassword}
                            onChange={handlePasswordChange}
                            error={passwordErrors.currentPassword}
                          />
                          <Input
                            label="New Password"
                            name="newPassword"
                            type="password"
                            value={passwordData.newPassword}
                            onChange={handlePasswordChange}
                            error={passwordErrors.newPassword}
                          />
                          <Input
                            label="Confirm New Password"
                            name="confirmPassword"
                            type="password"
                            value={passwordData.confirmPassword}
                            onChange={handlePasswordChange}
                            error={passwordErrors.confirmPassword}
                          />
                          <div className="d-flex justify-content-end">
                            <Button
                              type="submit"
                              variant="secondary"
                              isLoading={isLoading}
                            >
                              Change Password
                            </Button>
                          </div>
                        </form>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;
