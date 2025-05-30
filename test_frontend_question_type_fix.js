/**
 * Test script to manually test the fix for question type and specialization in the frontend
 * Run this in your browser's developer console on the question creation/edit pages
 */

(function() {
  console.group('Testing Question Type & Specialization Fix');
  console.log('This script validates that question type and specialization are properly separated');
  
  // Get current URL to determine what page we're on
  const currentPath = window.location.pathname;
  
  if (!currentPath.includes('question-bank')) {
    console.error('Please run this script on a question bank page');
    console.groupEnd();
    return;
  }

  // Check if required fields exist in the UI
  function checkFields() {
    const questionTypeSelect = document.getElementById('questionType');
    const specializationSelect = document.getElementById('specialization');
    
    console.log('Question Type Select:', questionTypeSelect ? 'Found ✓' : 'Missing ✗');
    console.log('Specialization Select:', specializationSelect ? 'Found ✓' : 'Missing ✗');
    
    if (!questionTypeSelect || !specializationSelect) {
      console.warn('Cannot find both fields, may be using old version or on wrong page');
      return false;
    }
    
    // Check if question type has correct options
    const questionTypeOptions = Array.from(questionTypeSelect.options).map(opt => opt.value);
    console.log('Question Type Options:', questionTypeOptions);
    
    const hasMultipleChoice = questionTypeOptions.includes('multiple_choice');
    const hasReadingComprehension = questionTypeOptions.includes('reading_comprehension');
    const hasTyping = questionTypeOptions.includes('typing');
    
    console.log('Has Multiple Choice:', hasMultipleChoice ? 'Yes ✓' : 'No ✗');
    console.log('Has Reading Comprehension:', hasReadingComprehension ? 'Yes ✓' : 'No ✗');
    console.log('Has Typing Test:', hasTyping ? 'Yes ✓' : 'No ✗');
    
    // Check if specialization has correct options
    const specializationOptions = Array.from(specializationSelect.options).map(opt => opt.value);
    console.log('Specialization Options:', specializationOptions);
    
    const hasAptitude = specializationOptions.includes('aptitude');
    const hasVerbal = specializationOptions.includes('verbal');
    const hasQuantitative = specializationOptions.includes('quantitative');
    
    console.log('Has Aptitude:', hasAptitude ? 'Yes ✓' : 'No ✗');
    console.log('Has Verbal:', hasVerbal ? 'Yes ✓' : 'No ✗');
    console.log('Has Quantitative:', hasQuantitative ? 'Yes ✓' : 'No ✗');
    
    return hasMultipleChoice && hasReadingComprehension && hasTyping && 
           hasAptitude && hasVerbal && hasQuantitative;
  }
  
  // If we're on the question dashboard page, test the filters
  function testDashboardFilters() {
    const questionTypeSelect = document.getElementById('questionType');
    const specializationSelect = document.getElementById('specialization');
    
    if (!questionTypeSelect || !specializationSelect) {
      console.warn('Cannot find both filter fields');
      return;
    }
    
    console.log('Testing dashboard filters...');
    
    // Test setting each filter independently
    console.log('Testing question type filter...');
    questionTypeSelect.value = 'multiple_choice';
    questionTypeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    
    console.log('Testing specialization filter...');
    specializationSelect.value = 'aptitude';
    specializationSelect.dispatchEvent(new Event('change', { bubbles: true }));
    
    console.log('Both filters set, check network tab for API requests');
    console.log('Expected API parameters: question_type=multiple_choice&specialization=aptitude');
  }
  
  // If we're on the question creation page, test the form
  function testQuestionForm() {
    const questionTypeSelect = document.getElementById('questionType');
    const specializationSelect = document.getElementById('specialization');
    
    if (!questionTypeSelect || !specializationSelect) {
      console.warn('Cannot find both form fields');
      return;
    }
    
    console.log('Testing question form...');
    
    // Test setting incompatible values to trigger validation
    console.log('Testing validation for typing test with quantitative specialization...');
    questionTypeSelect.value = 'typing';
    questionTypeSelect.dispatchEvent(new Event('change', { bubbles: true }));
    
    specializationSelect.value = 'quantitative';
    specializationSelect.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Try submitting to trigger validation
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
      console.log('Attempting to submit to trigger validation...');
      // Just trigger form validation without actual submission
      const form = submitButton.closest('form');
      if (form) {
        form.reportValidity();
      }
    }
  }
  
  // Run appropriate tests based on the current page
  if (currentPath.includes('/create') || currentPath.includes('/edit')) {
    console.log('Detected question form page');
    if (checkFields()) {
      testQuestionForm();
    }
  } else {
    console.log('Detected question dashboard page');
    if (checkFields()) {
      testDashboardFilters();
    }
  }
  
  console.log('Test script completed');
  console.groupEnd();
})();
