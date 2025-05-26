// This is a Cypress test for testing the question edit functionality.
// You would need to install and configure Cypress in your project first.

describe('Question Edit Functionality', () => {
  beforeEach(() => {
    // Login as admin before each test
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@planventure.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Wait for login to complete
    cy.url().should('include', '/dashboard');
  });

  it('should load question details for editing', () => {
    // Navigate to questions page
    cy.visit('/assessments/questions');
    
    // Find a question and click edit
    cy.get('.question-item').first().find('.edit-button').click();
    
    // Verify we're on the edit page
    cy.url().should('include', '/assessments/questions/edit/');
    
    // Check that form is loaded with question data
    cy.get('#content').should('not.be.empty');
    cy.get('#difficulty').should('exist');
  });

  it('should successfully edit a question', () => {
    // Navigate directly to edit page of a known question
    // Replace 1 with an actual question ID from your database
    cy.visit('/assessments/questions/edit/1');
    
    // Change question content
    const newQuestionText = 'Updated question content ' + Date.now();
    cy.get('#content').clear().type(newQuestionText);
    
    // Change difficulty
    cy.get('#difficulty').select('hard');
    
    // Change time limit
    cy.get('#time_limit').clear().type('90');
    
    // For multiple choice questions, add and edit options
    cy.get('.btn-outline-secondary').contains('Add Option').click();
    cy.get('input[placeholder="Option 4"]').type('New option text');
    
    // Save changes
    cy.get('button[type="submit"]').contains('Save Changes').click();
    
    // Verify we're redirected back to questions page
    cy.url().should('include', '/assessments/questions');
    
    // Verify toast message appears
    cy.get('.Toastify__toast-body').should('contain', 'Question updated successfully');
    
    // Verify changes are visible in the questions list
    // This may not be feasible if the questions list doesn't show full content
  });

  it('should show validation errors when form is invalid', () => {
    cy.visit('/assessments/questions/edit/1');
    
    // Clear required field
    cy.get('#content').clear();
    
    // Try to save
    cy.get('button[type="submit"]').contains('Save Changes').click();
    
    // Verify error message appears
    cy.get('.Toastify__toast-body').should('contain', 'Question content is required');
    
    // Verify we stay on the edit page
    cy.url().should('include', '/assessments/questions/edit/');
  });

  it('should handle API errors gracefully', () => {
    // This test would need to mock a failed API response
    // Requires Cypress network interception setup
    cy.visit('/assessments/questions/edit/1');
    
    cy.intercept('PUT', '/api/questions/*', {
      statusCode: 500,
      body: { error: 'Server error' }
    }).as('updateQuestion');
    
    // Make a change
    cy.get('#content').clear().type('Content that will trigger an error');
    
    // Submit the form
    cy.get('button[type="submit"]').contains('Save Changes').click();
    
    // Verify API called and error message shown
    cy.wait('@updateQuestion');
    cy.get('.Toastify__toast-body').should('contain', 'Server error');
    
    // Verify we stay on the edit page
    cy.url().should('include', '/assessments/questions/edit/');
  });
});
