import { useState, useEffect } from 'react';
import { 
  QUESTION_TYPES, 
  SPECIALIZATIONS, 
  getRecommendationMessage 
} from '../utils/questionValidation';

/**
 * A custom hook to help with validation of question type and specialization combinations
 * 
 * @param {string} questionType - The question type (format)
 * @param {string} specialization - The specialization (subject area)
 * @returns {Object} - An object containing validation state and helper functions
 */
export const useQuestionTypeValidation = (initialQuestionType, initialSpecialization) => {
  const [questionType, setQuestionType] = useState(initialQuestionType || QUESTION_TYPES.MULTIPLE_CHOICE);
  const [specialization, setSpecialization] = useState(initialSpecialization || SPECIALIZATIONS.APTITUDE);
  const [warning, setWarning] = useState(null);

  // Update warning message when either value changes
  useEffect(() => {
    const message = getRecommendationMessage(questionType, specialization);
    setWarning(message);
  }, [questionType, specialization]);

  /**
   * Update the question type (format)
   * @param {string} newType - The new question type value
   */
  const updateQuestionType = (newType) => {
    setQuestionType(newType);
  };

  /**
   * Update the specialization (subject area)
   * @param {string} newSpecialization - The new specialization value
   */
  const updateSpecialization = (newSpecialization) => {
    setSpecialization(newSpecialization);
  };

  /**
   * Automatically suggest the best specialization for the given question type
   * @returns {string} - The suggested specialization
   */
  const suggestSpecialization = () => {
    switch (questionType) {
      case QUESTION_TYPES.MULTIPLE_CHOICE:
        return specialization !== SPECIALIZATIONS.TYPING && 
               specialization !== 'typing' && 
               specialization !== 'reading_comprehension' ? 
                specialization : SPECIALIZATIONS.APTITUDE;
      
      case QUESTION_TYPES.READING_COMPREHENSION:
        return SPECIALIZATIONS.VERBAL;
      
      case QUESTION_TYPES.TYPING:
        return SPECIALIZATIONS.TECHNICAL;
      
      default:
        return SPECIALIZATIONS.APTITUDE;
    }
  };

  return {
    questionType,
    specialization,
    warning,
    updateQuestionType,
    updateSpecialization,
    suggestSpecialization
  };
};

export default useQuestionTypeValidation;
