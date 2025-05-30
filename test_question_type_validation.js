/**
 * Test script for question type and specialization validation in PlanVenture
 * 
 * This script tests the following:
 * 1. Validation rules for different question types
 * 2. Recommended combinations of question types and specializations
 * 3. Warning messages for uncommon combinations
 */

// Sample questions to test validation
const testQuestions = [
  // Valid combinations
  {
    id: 'valid-multiple-choice',
    question_type: 'multiple_choice',
    specialization: 'aptitude',
    content: 'What is the capital of France?',
    options: ['London', 'Paris', 'Berlin', 'Madrid'],
    correct_answer: 'Paris',
    difficulty: 'easy'
  },
  {
    id: 'valid-reading-comprehension',
    question_type: 'reading_comprehension',
    specialization: 'verbal',
    content: 'Based on the passage above, what can be inferred about the main character?',
    reading_set: {
      content: 'Long reading passage about a character...'
    },
    difficulty: 'medium'
  },
  {
    id: 'valid-typing',
    question_type: 'typing',
    specialization: 'technical',
    content: 'The quick brown fox jumps over the lazy dog. This is a typing test that requires candidates to accurately reproduce this text.',
    difficulty: 'medium'
  },
  
  // Invalid combinations - should trigger warnings
  {
    id: 'uncommon-typing',
    question_type: 'typing',
    specialization: 'verbal',  // Uncommon combination
    content: 'The quick brown fox jumps over the lazy dog. This is a typing test.',
    difficulty: 'easy'
  },
  {
    id: 'uncommon-reading-comprehension',
    question_type: 'reading_comprehension',
    specialization: 'programming',  // Uncommon combination
    content: 'Based on the code snippet above, what will be output?',
    reading_set: {
      content: 'Code snippet...'
    },
    difficulty: 'hard'
  },
  
  // Invalid due to missing fields
  {
    id: 'invalid-missing-content',
    question_type: 'multiple_choice',
    specialization: 'aptitude',
    content: '',  // Empty content
    options: ['Option 1', 'Option 2'],
    correct_answer: 'Option 1',
    difficulty: 'easy'
  },
  {
    id: 'invalid-missing-options',
    question_type: 'multiple_choice',
    specialization: 'aptitude',
    content: 'This is a question with no options.',
    options: [],  // Empty options
    difficulty: 'easy'
  },
  {
    id: 'invalid-missing-reading-passage',
    question_type: 'reading_comprehension',
    specialization: 'verbal',
    content: 'Question about a missing passage.',
    // Missing reading_set
    difficulty: 'medium'
  },
  {
    id: 'invalid-short-typing',
    question_type: 'typing',
    specialization: 'technical',
    content: 'Too short',  // Less than 50 chars
    difficulty: 'easy'
  }
];

/**
 * Test for dashboard filtering
 */
const testDashboardFiltering = () => {
  console.group('🧪 Testing Dashboard Filtering');
  
  // Simulate dashboard filter combinations
  const filterCombinations = [
    { questionType: '', specialization: '', expected: true },
    { questionType: 'multiple_choice', specialization: '', expected: true },
    { questionType: '', specialization: 'aptitude', expected: true },
    { questionType: 'multiple_choice', specialization: 'aptitude', expected: true },
    { questionType: 'reading_comprehension', specialization: 'verbal', expected: true },
    { questionType: 'typing', specialization: 'technical', expected: true },
    { questionType: 'typing', specialization: 'verbal', expected: false },
    { questionType: 'reading_comprehension', specialization: 'programming', expected: false }
  ];
  
  // Import the validation function
  const { isRecommendedCombination } = require('./planventure-web/src/utils/questionValidation');
  
  filterCombinations.forEach((combo, index) => {
    const { questionType, specialization, expected } = combo;
    const result = isRecommendedCombination(questionType, specialization);
    
    const testResult = result === expected;
    console.log(`Test ${index + 1}: ${testResult ? '✅ PASS' : '❌ FAIL'} - Type: ${questionType || 'All'}, Specialization: ${specialization || 'All'}`);
    if (!testResult) {
      console.error('  Expected:', expected, 'Got:', result);
    }
  });
  
  console.groupEnd();
}

/**
 * Test the question bank dashboard component
 */
const testQuestionBankDashboard = () => {
  console.group('🧪 Testing QuestionBankDashboard Component');
  
  // Test the getFilterCompatibilityMessage function
  const { getRecommendationMessage } = require('./planventure-web/src/utils/questionValidation');
  
  const messageCombinations = [
    { type: 'multiple_choice', spec: 'aptitude', expectMessage: false },
    { type: 'reading_comprehension', spec: 'verbal', expectMessage: false },
    { type: 'typing', spec: 'technical', expectMessage: false },
    { type: 'typing', spec: 'verbal', expectMessage: true },
    { type: 'reading_comprehension', spec: 'programming', expectMessage: true }
  ];
  
  messageCombinations.forEach((combo, index) => {
    const { type, spec, expectMessage } = combo;
    const message = getRecommendationMessage(type, spec);
    const hasMessage = message !== null;
    
    const testResult = hasMessage === expectMessage;
    console.log(`Test ${index + 1}: ${testResult ? '✅ PASS' : '❌ FAIL'} - Type: ${type}, Specialization: ${spec}`);
    console.log(`  Message: ${message || '(none)'}`);
  });
  
  console.groupEnd();
}

/**
 * Run validation tests for all test questions
 */
function runTests() {
  console.group('🧪 Running Question Type & Specialization Validation Tests');
  
  let passCount = 0;
  let warningCount = 0;
  
  // Test the dashboard filtering
  testDashboardFiltering();
    // Test the question bank dashboard component
  testQuestionBankDashboard();
  let failCount = 0;
  
  // Check if we're in a browser or Node environment
  const isBrowser = typeof window !== 'undefined';
  
  // Import validation utils if available in browser environment or use mock implementation
  const validationUtils = (isBrowser && window.questionValidation) ? window.questionValidation : {
    // Mock implementation for standalone testing
    validateQuestion: (question) => {
      const errors = [];
      
      // Basic validation
      if (!question.content || question.content.trim() === '') {
        errors.push('Question content is required');
      }
      
      // Question type-specific validation
      if (question.question_type === 'multiple_choice') {
        if (!Array.isArray(question.options) || question.options.length < 2) {
          errors.push('Multiple choice questions require at least 2 options');
        }
        if (!question.correct_answer) {
          errors.push('Multiple choice questions must have a correct answer');
        }
      } else if (question.question_type === 'reading_comprehension') {
        if (!question.reading_set || !question.reading_set.content) {
          errors.push('Reading comprehension questions require a reading passage');
        }
      } else if (question.question_type === 'typing') {
        if (question.content && question.content.length < 50) {
          errors.push('Typing tests require at least 50 characters');
        }
      }
      
      // Combination validation
      const uncommonCombinations = {
        'typing': ['verbal', 'quantitative', 'logical', 'analytics'],
        'reading_comprehension': ['technical', 'programming', 'analytics']
      };
      
      const uncommonList = uncommonCombinations[question.question_type] || [];
      if (uncommonList.includes(question.specialization)) {
        errors.push(`Uncommon combination: ${question.question_type} with ${question.specialization}`);
      }
      
      return {
        isValid: errors.length === 0,
        errors
      };
    }
  };
  
  testQuestions.forEach(question => {
    const { isValid, errors } = validationUtils.validateQuestion(question);
    
    console.group(`📋 Test: ${question.id}`);
    console.log('Question Type:', question.question_type);
    console.log('Specialization:', question.specialization);
    
    if (isValid) {
      console.log('✅ PASS: Valid question');
      passCount++;
    } else if (errors.length === 1 && errors[0].includes('Uncommon combination')) {
      console.log('⚠️ WARNING: ' + errors[0]);
      warningCount++;
    } else {
      console.log('❌ FAIL: Invalid question');
      console.log('Errors:', errors);
      failCount++;
    }
    console.groupEnd();
  });
  
  console.group('📊 Results Summary');
  console.log(`✅ Passed: ${passCount}`);
  console.log(`⚠️ Warnings: ${warningCount}`);
  console.log(`❌ Failed: ${failCount}`);
  console.log(`Total: ${testQuestions.length}`);
  console.groupEnd();
  
  console.groupEnd();
}

// Run tests
if (typeof window !== 'undefined') {
  // Browser environment
  window.addEventListener('load', () => {
    console.log('Running tests in browser environment...');
    runTests();
  });
} else {
  // Node.js environment
  console.log('Running tests in Node.js environment...');
  runTests();
}

// Export for module usage
if (typeof module !== 'undefined') {
  module.exports = {
    testQuestions,
    runTests
  };
}
