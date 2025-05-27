

import React from 'react';

const Button = ({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  className = '', 
  disabled = false,
  isLoading = false,
  ...props 
}) => {
  const baseClasses = 'btn';
    const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    light: 'btn-light',
    outline: 'btn-outline-primary',
    'outline-danger': 'btn-outline-danger',
  };

  const loadingSpinner = (
    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
  );

  return (
    <button
      type={type}
      className={`${baseClasses} ${variantClasses[variant] || 'btn-primary'} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && loadingSpinner}
      {isLoading ? 'Loading...' : children}
    </button>
  );
};

export default Button;
