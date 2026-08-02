import React from 'react';
import { Link } from 'react-router-dom';

function LoginButton() {
  return (
    <Link to="/login" className="btn btn-primary">
      Login
    </Link>
  );
}

function SignupButton() {
  return (
    <Link to="/register" className="btn btn-secondary">
      Sign Up
    </Link>
  );
}

export { LoginButton, SignupButton };
