import React from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import Navigation from '../Navigation';
import QuestionForm from '../questionbank/QuestionForm';

const EditQuestion = () => {
  const { questionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extract the returnTo path from URL search params if it exists
  const searchParams = new URLSearchParams(location.search);
  const returnTo = searchParams.get('returnTo') || '/question-bank';
  
  const handleSuccess = () => {
    // After successful update, navigate to the returnTo path
    navigate(returnTo);
  };
  
  return (
    <div className="min-vh-100 bg-light">
      <Navigation />
      
      <div className="container py-4">
        <QuestionForm mode="edit" questionId={questionId} onSuccess={handleSuccess} />
      </div>
    </div>
  );
};

export default EditQuestion;
