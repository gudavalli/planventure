
/**
 * Utility functions for validating question types and specializations
 */

/**
 * Valid question types
 */
export const QUESTION_TYPES = {
  MULTIPLE_CHOICE: 'multiple_choice',
  READING_COMPREHENSION: 'reading_comprehension',
  TYPING: 'typing'
};

/**
 * Valid specializations (subject areas)
 */
export const SPECIALIZATIONS = {
  APTITUDE: 'aptitude',
  VERBAL: 'verbal',
  QUANTITATIVE: 'quantitative',
  LOGICAL: 'logical',
  TECHNICAL: 'technical',
  PROGRAMMING: 'programming',
  ANALYTICS: 'analytics'
};

/**
 * Recommended specializations for each question type
 */
export const RECOMMENDED_SPECIALIZATIONS = {
  [QUESTION_TYPES.MULTIPLE_CHOICE]: [
    SPECIALIZATIONS.APTITUDE,
    SPECIALIZATIONS.VERBAL,
    SPECIALIZATIONS.QUANTITATIVE,
    SPECIALIZATIONS.LOGICAL,
    SPECIALIZATIONS.TECHNICAL,
    SPECIALIZATIONS.PROGRAMMING,
    SPECIALIZATIONS.ANALYTICS
  ],
  [QUESTION_TYPES.READING_COMPREHENSION]: [
    SPECIALIZATIONS.VERBAL,
    SPECIALIZATIONS.APTITUDE,
    SPECIALIZATIONS.LOGICAL
  ],
  [QUESTION_TYPES.TYPING]: [
    SPECIALIZATIONS.APTITUDE,
    SPECIALIZATIONS.TECHNICAL,
    SPECIALIZATIONS.PROGRAMMING
  ]
};

/**
 * Check if a question type and specialization combination is recommended
 * @param {string} questionType - The question type
 * @param {string} specialization - The specialization (subject area)
 * @returns {boolean} - True if the combination is recommended
 */
export const isRecommendedCombination = (questionType, specialization) => {
  if (!questionType || !specialization) return true;
  
  const recommendedForType = RECOMMENDED_SPECIALIZATIONS[questionType] || [];
  return recommendedForType.includes(specialization);
};

/**
 * Get recommendation message for a question type and specialization combination
 * @param {string} questionType - The question type
 * @param {string} specialization - The specialization (subject area)
 * @returns {string|null} - A message if the combination is not recommended, null otherwise
 */
export const getRecommendationMessage = (questionType, specialization) => {
  if (!questionType || !specialization) return null;
  
  if (!isRecommendedCombination(questionType, specialization)) {
    const recommendedList = (RECOMMENDED_SPECIALIZATIONS[questionType] || [])
      .map(spec => {
        // Convert the specialization value to a readable format
        switch(spec) {
          case SPECIALIZATIONS.APTITUDE: return 'Aptitude';
          case SPECIALIZATIONS.VERBAL: return 'Verbal';
          case SPECIALIZATIONS.QUANTITATIVE: return 'Quantitative';
          case SPECIALIZATIONS.LOGICAL: return 'Logical';
          case SPECIALIZATIONS.TECHNICAL: return 'Technical';
          case SPECIALIZATIONS.PROGRAMMING: return 'Programming';
          case SPECIALIZATIONS.ANALYTICS: return 'Analytics';
          default: return spec;
        }
      })
      .join(', ');
    
    // Convert the question type to a readable format
    let readableType = questionType;
    switch(questionType) {
      case QUESTION_TYPES.MULTIPLE_CHOICE: 
        readableType = 'Multiple Choice';
        break;
      case QUESTION_TYPES.READING_COMPREHENSION:
        readableType = 'Reading Comprehension';
        break;
      case QUESTION_TYPES.TYPING:
        readableType = 'Typing Test';
        break;
    }
    
    return `This specialization is not typically used with ${readableType} questions. Recommended specializations: ${recommendedList}.`;
  }
  
  return null;
};

/**
 * Validate that a question object has all required fields and valid combinations
 * @param {Object} question - The question object to validate
 * @returns {Object} - Object with isValid boolean and errors array
 */
export const validateQuestion = (question) => {
  const errors = [];
  
  // Check required fields
  if (!question.content) {
    errors.push('Question content is required');
  }
  
  if (!question.question_type) {
    errors.push('Question format is required');
  } else if (!Object.values(QUESTION_TYPES).includes(question.question_type)) {
    errors.push(`Invalid question format: ${question.question_type}`);
  }
  
  if (!question.specialization) {
    errors.push('Subject area is required');
  } else if (!Object.values(SPECIALIZATIONS).includes(question.specialization)) {
    errors.push(`Invalid subject area: ${question.specialization}`);
  }
  
  // Check type-specific requirements
  if (question.question_type === QUESTION_TYPES.MULTIPLE_CHOICE) {
    if (!Array.isArray(question.options) || question.options.filter(opt => opt.trim()).length < 2) {
      errors.push('Multiple choice questions require at least 2 options');
    }
    
    if (!question.correct_answer) {
      errors.push('Multiple choice questions must have a correct answer');
    }
  }
  
  if (question.question_type === QUESTION_TYPES.TYPING && question.content && question.content.length < 50) {
    errors.push('Typing tests must have at least 50 characters of content');
  }
  
  // Check for recommended combinations
  const recommendationMessage = getRecommendationMessage(question.question_type, question.specialization);
  if (recommendationMessage) {
    errors.push(recommendationMessage);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
