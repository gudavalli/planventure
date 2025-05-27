import React from 'react';

const FormError = ({ message }) => {
  if (!message) return null;
  
  return (
    <div className="alert alert-danger mb-3 animate__animated animate__shakeX" role="alert">
      <i className="bi bi-exclamation-triangle-fill me-2"></i>
      {message}
    </div>
  );
};

export default FormError;
