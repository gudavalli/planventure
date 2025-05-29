import React from 'react';
import { Link } from 'react-router-dom';
import Navigation from '../Navigation';
import QuestionForm from '../questionbank/QuestionForm';

const CreateQuestion = () => {
  const handleSuccess = () => {
    // After successful creation, navigate to question bank
    // The QuestionForm component will handle this automatically
  };
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <QuestionForm mode="create" onSuccess={handleSuccess} />
      </div>
    </div>
  );
};

export default CreateQuestion;
