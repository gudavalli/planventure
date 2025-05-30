# Question Type and Specialization Cleanup Plan

## Overview
This document outlines the remaining tasks to fully complete the question type and specialization separation in the PlanVenture assessment system.

## Priority Tasks

### 1. Harmonize Dashboard Components
There are currently two versions of the QuestionBankDashboard component:
- `src/components/questionbank/QuestionBankDashboard.jsx` - Fully updated
- `src/components/assessment/QuestionBankDashboard.jsx` - Using old approach

**Action Items:**
- Determine which component should be the canonical version
- Update the outdated component to match the new question type/specialization approach
- Consider consolidating to a single component if both are needed

### 2. Update API Documentation
As mentioned in the QUESTION_TYPE_SPECIALIZATION_FIX_COMPLETE.md file, API documentation needs to be updated.

**Action Items:**
- Document all question-related API endpoints with the new field structure
- Include examples of filtering by both question_type and specialization
- Update any Swagger/OpenAPI specifications if used

### 3. Complete Manual Testing
Execute the manual test plan outlined in QUESTION_TYPE_FIX_TEST_SUMMARY.md.

**Action Items:**
- Test the create question flow with all question types and various specializations
- Test the edit question flow to ensure both fields are preserved correctly
- Verify filtering functionality by question type and specialization
- Test API responses to ensure both fields are returned correctly

### 4. Fix Test Script Issues
The test_question_type_validation.js script has an error when running in Node.js environment.

**Action Items:**
- Update the script to handle both browser and Node.js environments
- Replace references to window object with conditional checks
- Consider creating a separate Node.js version if needed

### 5. Integration Testing
Ensure the backend and frontend changes work correctly together.

**Action Items:**
- Test the API and UI together to verify correct behavior
- Check for any edge cases in the type/specialization combinations
- Verify backward compatibility with existing code

## Optional Improvements

### 1. Enhanced Validation Rules
Consider adding validation rules for valid question_type and specialization combinations.

**Action Items:**
- Define "strong" validation rules that guide users toward recommended combinations
- Update the frontend components to provide guidance without blocking valid choices

### 2. User Interface Enhancements
Further improve the UI to make the distinction between question types and specializations clearer.

**Action Items:**
- Add tooltips explaining the difference between the fields
- Consider visual indicators for recommended combinations
- Update the question display to clearly show both attributes

### 3. Reporting Improvements
Update reporting features to leverage the separation between question types and specializations.

**Action Items:**
- Add new analytics views that break down questions by both dimensions
- Create visualizations showing the distribution of questions across types and specializations

## Timeline
- Priority Tasks: Complete within 1-2 weeks
- Optional Improvements: Implement in future sprints based on user feedback

## Success Criteria
- All components consistently use the new approach
- Documentation is updated and accurate
- All test cases pass
- Users can successfully create, edit, and filter questions using both fields
- No confusion between question types and specializations in the UI
