const Input = ({ 
  label,
  type = 'text',
  error,
  className = '',
  ...props
}) => {
  const inputId = `input-${Math.random().toString(36).substring(2, 9)}`;
  
  return (
    <div className="mb-3">
      {label && (
        <label htmlFor={inputId} className="form-label">
          {label}
        </label>
      )}
      <input
        id={inputId}
        type={type}
        className={`form-control ${error ? 'is-invalid' : ''} ${className}`}
        {...props}
      />
      {error && (
        <div className="invalid-feedback">
          {error}
        </div>
      )}
    </div>
  );
};

export default Input;
