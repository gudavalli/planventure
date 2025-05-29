import React from 'react';
import { useParams, Link } from 'react-router-dom';
import Navigation from '../Navigation';
import QuestionForm from './QuestionForm';

const QuestionBankEditQuestion = () => {
  const { questionId } = useParams();

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <div className="pt-20 pb-12">
        <div className="max-w-4xl mx-auto px-4">          {/* Breadcrumb */}
          <div className="mb-6">
            <nav aria-label="Breadcrumb">
              <div className="flex items-center text-sm text-gray-600">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-blue-600"
                >
                  Dashboard
                </Link>
                <span className="mx-2 text-gray-400">/</span>
                <Link
                  to="/question-bank"
                  className="text-gray-700 hover:text-blue-600"
                >
                  Question Bank
                </Link>
                <span className="mx-2 text-gray-400">/</span>
                <span className="text-gray-500">
                  Edit Question
                </span>
              </div>
            </nav>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Edit Question</h1>
            <QuestionForm mode="edit" questionId={questionId} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionBankEditQuestion;
