import { useState } from 'react';
import Navigation from '../components/Navigation';
import Button from '../components/Button';
import Input from '../components/Input';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    phone: user?.phone || '',
  });
  const [isLoading, setIsLoading] = useState(false);
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
      await updateProfile({
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone: formData.phone,
      });
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
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
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      
      <main className="py-10">
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
          <div className="space-y-6">
            {/* Profile Section */}
            <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
              <div className="md:grid md:grid-cols-3 md:gap-6">
                <div className="md:col-span-1">
                  <h3 className="text-lg font-medium leading-6 text-gray-900">Profile</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Update your personal information.
                  </p>
                </div>
                <div className="mt-5 md:col-span-2 md:mt-0">
                  <form onSubmit={handleProfileSubmit}>
                    <div className="grid grid-cols-6 gap-6">
                      <div className="col-span-6 sm:col-span-3">
                        <Input
                          label="First Name"
                          name="firstName"
                          type="text"
                          value={formData.firstName}
                          onChange={handleProfileChange}
                        />
                      </div>
                      <div className="col-span-6 sm:col-span-3">
                        <Input
                          label="Last Name"
                          name="lastName"
                          type="text"
                          value={formData.lastName}
                          onChange={handleProfileChange}
                        />
                      </div>
                      <div className="col-span-6 sm:col-span-3">
                        <Input
                          label="Phone Number"
                          name="phone"
                          type="tel"
                          value={formData.phone}
                          onChange={handleProfileChange}
                        />
                      </div>
                    </div>
                    <div className="mt-5 flex justify-end">
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

            {/* Password Section */}
            <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
              <div className="md:grid md:grid-cols-3 md:gap-6">
                <div className="md:col-span-1">
                  <h3 className="text-lg font-medium leading-6 text-gray-900">Password</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Update your password.
                  </p>
                </div>
                <div className="mt-5 md:col-span-2 md:mt-0">
                  <form onSubmit={handlePasswordSubmit}>
                    <div className="space-y-4">
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
                    </div>
                    <div className="mt-5 flex justify-end">
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
      </main>
    </div>
  );
};

export default Profile;
