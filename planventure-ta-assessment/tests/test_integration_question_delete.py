import json
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

@pytest.mark.integration
def test_delete_question_integration(app, setup_database):
    """
    Test the full flow of deleting a question from a template using the UI
    
    This test requires:
    - Chrome WebDriver
    - Running frontend and backend servers
    """
    # Skip this test unless explicitly run with --integration flag
    pytest.skip("Integration test - run only with --integration flag")
    
    # Set up Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create a template and question first using the API
    with app.test_client() as client:
        # Login as admin
        client.post('/api/auth/login', 
                    data=json.dumps({'email': 'admin@example.com', 'password': 'admin123'}),
                    content_type='application/json')
        
        # Create template
        template_data = {
            'name': 'Integration Test Template',
            'description': 'Testing question deletion integration',
            'time_limit': 60,
            'percentage': 100,
            'creator_id': 1
        }
        
        template_response = client.post('/api/templates',
                                       data=json.dumps(template_data),
                                       content_type='application/json')
        template_id = json.loads(template_response.data)['id']
        
        # Create a question
        question_data = {
            'specialization': 'aptitude',
            'content': 'Integration test question',
            'options': ['A', 'B', 'C', 'D'],
            'correct_answer': 'A'
        }
        
        question_response = client.post('/api/questions',
                                      data=json.dumps(question_data),
                                      content_type='application/json')
        question_id = json.loads(question_response.data)['id']
        
        # Add question to template
        client.post(f'/api/templates/{template_id}/questions',
                   data=json.dumps({'question_ids': [question_id]}),
                   content_type='application/json')
    
    # Now use Selenium to test the UI flow
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to login page
        driver.get("http://localhost:3000/login")
        
        # Login
        driver.find_element(By.ID, "email").send_keys("admin@example.com")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for redirect after login
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # Navigate to the template details page
        driver.get(f"http://localhost:3000/assessments/templates/{template_id}")
        
        # Wait for template details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Integration Test Template')]"))
        )
        
        # Find and click delete button for the question
        delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-outline-danger"))
        )
        delete_button.click()
        
        # Wait for confirmation modal
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//h5[contains(text(), 'Confirm Removal')]"))
        )
        
        # Click confirm button to delete
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Remove Question')]"))
        )
        confirm_button.click()
        
        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Question removed')]"))
        )
        
        # Verify question was deleted (should not be in the page anymore)
        assert "Integration test question" not in driver.page_source
        
    finally:
        driver.quit()
        
    # Verify on the server side that the question was removed
    with app.test_client() as client:
        client.post('/api/auth/login', 
                    data=json.dumps({'email': 'admin@example.com', 'password': 'admin123'}),
                    content_type='application/json')
        
        response = client.get(f'/api/templates/{template_id}')
        data = json.loads(response.data)
        
        # Template should not have any questions
        assert len(data['questions']) == 0
