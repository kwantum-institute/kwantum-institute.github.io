import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import RegisterForm from '../components/RegisterForm';
import { useAuth } from '../components/AuthContext';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { isAuthenticated, loading } = useAuth();

  // If user is already authenticated, redirect to home
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="auth-form-container">
        <div className="auth-form">
          <div className="auth-form-header">
            <h2>Loading...</h2>
          </div>
        </div>
      </div>
    );
  }

  const handleSwitchToRegister = () => {
    setIsLogin(false);
  };

  const handleSwitchToLogin = () => {
    setIsLogin(true);
  };

  const handleClose = () => {
    // Redirect to home after successful authentication
    window.location.href = '/';
  };

  return (
    <>
      {isLogin ? (
        <LoginForm 
          onSwitchToRegister={handleSwitchToRegister}
          onClose={handleClose}
        />
      ) : (
        <RegisterForm 
          onSwitchToLogin={handleSwitchToLogin}
          onClose={handleClose}
        />
      )}
    </>
  );
};

export default Login; 