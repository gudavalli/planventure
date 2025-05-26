# Create Question UI - Correct Answer Selection Fix

## Problem Identified
The Create Question UI had an issue where the correct answer selection (radio buttons) would become unchecked when users modified the option text. This was happening because:

1. The radio buttons were checking `formData.correct_answer === option` (text comparison)
2. When users typed in option inputs, `handleOptionChange` updated the option text
3. But `correct_answer` still held the old text value
4. This caused the radio button to become unchecked when option text changed

## Solution Implemented
Changed the correct answer selection mechanism to use **option indexes** instead of **option text values**:

### Changes Made:

1. **Initial State**: Changed `correct_answer: ''` to `correct_answer: null`
2. **Radio Button Logic**: 
   - `checked={formData.correct_answer === index}` (instead of option text)
   - `onChange={() => setFormData(prev => ({ ...prev, correct_answer: index }))}` (instead of option text)
3. **Remove Option Function**: Updated to handle index-based correct answers properly
4. **Validation**: Updated to check for `null` instead of empty string
5. **Form Submission**: Convert index back to option text before sending to API

### Key Benefits:
- ✅ Radio button stays selected when option text is modified
- ✅ Proper handling when options are added/removed
- ✅ Maintains compatibility with existing API (sends option text)
- ✅ Consistent with EditQuestion component implementation

## Test Cases Covered:
1. Select correct answer → modify option text → radio button remains selected
2. Add new options → previous selection persists
3. Remove options → correct answer index adjusts appropriately
4. Validation works for missing correct answer selection
5. Form submission sends correct option text to API

## Files Modified:
- `c:\Users\sreen\learning\copilot-agent\planventure\planventure-web\src\components\assessment\CreateQuestion.jsx`

The fix ensures that the Create Question UI now properly handles correct answer selection for multiple choice questions, providing a smooth user experience when creating assessment questions.
