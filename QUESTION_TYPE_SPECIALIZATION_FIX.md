# Question Type vs Specialization Fix

## Overview
This documentation explains the changes made to fix the terminology confusion between question types and specializations in the PlanVenture assessment system.

## Problem
The system was using the term "specialization" in two different contexts:

1. As a **question format** (multiple choice, reading comprehension, typing)
2. As a **subject area** (aptitude, verbal, quantitative, logical, etc.)

This led to confusion in both the code and the user interface, making it difficult to properly categorize and filter questions.

## Solution
We implemented a fix that clearly separates these two concepts:

1. **Question Type/Format**: Represents the structure or format of the question
   - `multiple_choice` (previously "aptitude")
   - `reading_comprehension`
   - `typing`

2. **Specialization/Subject Area**: Represents the knowledge domain or subject
   - `aptitude`
   - `verbal`
   - `quantitative`
   - `logical`
   - `technical`
   - etc.

## Changes Made

### Backend Changes

1. **Database Schema Update**
   - Added a new `question_type` field to the `Question` model
   - Repurposed the existing `specialization` field to only represent subject areas

2. **Data Migration**
   - Created a migration script to populate the new `question_type` field based on existing data
   - Mapping:
     - "aptitude" → "multiple_choice"
     - "reading_comprehension" → "reading_comprehension"
     - "typing" → "typing"

3. **API Endpoint Updates**
   - Modified the `/questions` POST endpoint to handle both `question_type` and `specialization`
   - Updated the `/questions` GET endpoint to support filtering by both fields
   - Added backward compatibility to ensure existing client code continues to work

### Frontend Changes

1. **UI Clarifications**
   - Renamed "Question Type" to "Question Format" to better reflect its purpose
   - Updated "Specialization" label to "Subject Area/Specialization"
   - Enabled independent selection of both fields

2. **Data Handling**
   - Updated the `QuestionForm` component to manage both `question_type` and `specialization` independently
   - Modified form validation to check both fields
   - Updated API service to correctly map frontend values to backend expectations

3. **Type Mapping**
   - Maintained compatibility with existing code using a mapping system:
     ```javascript
     const typeMapping = {
       'aptitude': 'multiple_choice',
       'reading_comprehension': 'reading_comprehension',
       'typing': 'typing'
     };
     ```

## Testing
A test script (`test_question_type_fix.py`) was created to verify the fix, which tests:

1. Creating questions with different combinations of question types and specializations
2. Fetching questions with filters for both question type and specialization
3. Retrieving individual question details to ensure both fields are present
4. Updating questions to modify both fields independently

## Backward Compatibility
The changes were implemented to maintain backward compatibility:

1. The backend accepts the old format where "specialization" is used to represent question type
2. The frontend handles API responses that lack the new `question_type` field
3. Existing client code continues to work without modification

## Future Considerations
In the future, it might be beneficial to:

1. Update all client code to explicitly use the separate fields
2. Remove the backward compatibility layer once all clients are updated
3. Consider renaming the database field from `specialization` to `subject_area` for complete clarity
