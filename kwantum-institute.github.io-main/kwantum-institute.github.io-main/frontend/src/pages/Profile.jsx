import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../components/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user, profile, updateProfile, changePassword, logout, isAuthenticated, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    bio: profile?.bio || '',
    phone_number: profile?.phone_number || '',
    date_of_birth: profile?.date_of_birth || '',
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });

  // Redirect if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="profile-container">
        <div className="profile-loading">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      const result = await updateProfile(formData);
      setMessage(result.message);
      if (result.success) {
        setIsEditing(false);
      }
    } catch (error) {
      setMessage('An error occurred while updating your profile');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setMessage('');

    if (passwordData.new_password !== passwordData.new_password_confirm) {
      setMessage('New passwords do not match');
      return;
    }

    try {
      const result = await changePassword(passwordData);
      setMessage(result.message);
      if (result.success) {
        setIsChangingPassword(false);
        setPasswordData({
          old_password: '',
          new_password: '',
          new_password_confirm: '',
        });
      }
    } catch (error) {
      setMessage('An error occurred while changing your password');
    }
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Profile Settings</h1>
        <p>Manage your account and preferences</p>
      </div>

      <div className="profile-content">
        <div className="profile-sidebar">
          <button
            className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile Information
          </button>
          <button
            className={`tab-button ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => setActiveTab('security')}
          >
            Security
          </button>
          <button
            className={`tab-button ${activeTab === 'account' ? 'active' : ''}`}
            onClick={() => setActiveTab('account')}
          >
            Account
          </button>
        </div>

        <div className="profile-main">
          {message && (
            <div className={`profile-message ${message.includes('successfully') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Profile Information</h2>
                <button
                  className="edit-button"
                  onClick={() => setIsEditing(!isEditing)}
                >
                  {isEditing ? 'Cancel' : 'Edit'}
                </button>
              </div>

              <form onSubmit={handleProfileUpdate}>
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    value={user?.username || ''}
                    disabled
                    className="disabled-input"
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="disabled-input"
                  />
                </div>

                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={`${user?.first_name || ''} ${user?.last_name || ''}`.trim()}
                    disabled
                    className="disabled-input"
                  />
                </div>

                <div className="form-group">
                  <label>Bio</label>
                  <textarea
                    value={formData.bio}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    disabled={!isEditing}
                    placeholder="Tell us about yourself..."
                    rows={4}
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    disabled={!isEditing}
                    placeholder="Enter your phone number"
                  />
                </div>

                <div className="form-group">
                  <label>Date of Birth</label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    disabled={!isEditing}
                  />
                </div>

                {isEditing && (
                  <button type="submit" className="save-button">
                    Save Changes
                  </button>
                )}
              </form>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Security Settings</h2>
                <button
                  className="edit-button"
                  onClick={() => setIsChangingPassword(!isChangingPassword)}
                >
                  {isChangingPassword ? 'Cancel' : 'Change Password'}
                </button>
              </div>

              {isChangingPassword && (
                <form onSubmit={handlePasswordChange}>
                  <div className="form-group">
                    <label>Current Password</label>
                    <input
                      type="password"
                      value={passwordData.old_password}
                      onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                      placeholder="Enter your current password"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>New Password</label>
                    <input
                      type="password"
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                      placeholder="Enter your new password"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Confirm New Password</label>
                    <input
                      type="password"
                      value={passwordData.new_password_confirm}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password_confirm: e.target.value })}
                      placeholder="Confirm your new password"
                      required
                    />
                  </div>

                  <button type="submit" className="save-button">
                    Change Password
                  </button>
                </form>
              )}

              <div className="security-info">
                <h3>Account Security</h3>
                <p>Last login: {new Date().toLocaleDateString()}</p>
                <p>Email verification: {profile?.is_verified ? 'Verified' : 'Not verified'}</p>
              </div>
            </div>
          )}

          {activeTab === 'account' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Account Settings</h2>
              </div>

              <div className="account-info">
                <h3>Account Information</h3>
                <p><strong>Member since:</strong> {new Date(user?.date_joined).toLocaleDateString()}</p>
                <p><strong>Account status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
              </div>

              <div className="danger-zone">
                <h3>Danger Zone</h3>
                <p>These actions cannot be undone.</p>
                <button
                  className="logout-button"
                  onClick={handleLogout}
                >
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile; 