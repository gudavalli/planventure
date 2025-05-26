Write-Host "Testing Question Edit Navigation" -ForegroundColor Cyan

# Verify that the EditQuestion component properly handles returnTo parameter
Write-Host "1. Testing direct URL navigation with returnTo parameter" -ForegroundColor Yellow
Write-Host "Opening: http://localhost:5174/assessments/questions/1/edit?returnTo=%2Fassessments%2Ftemplates%2F1"
Write-Host "Expected behavior: After saving, should redirect to /assessments/templates/1"

# Verify that TemplateDetails -> View -> Edit -> Save works
Write-Host "`n2. Testing navigation flow: TemplateDetails -> View -> Edit -> Save" -ForegroundColor Yellow
Write-Host "Steps:"
Write-Host "a. Go to http://localhost:5174/assessments/templates/1"
Write-Host "b. Click 'View' for any question" 
Write-Host "c. Click 'Edit Question'" 
Write-Host "d. Make a change and click 'Save Changes'"
Write-Host "Expected behavior: Should return to the template details page"

# Verify that TemplateDetails -> Edit -> Save works
Write-Host "`n3. Testing navigation flow: TemplateDetails -> Edit -> Save" -ForegroundColor Yellow
Write-Host "Steps:"
Write-Host "a. Go to http://localhost:5174/assessments/templates/1"
Write-Host "b. Click 'Edit' for any question directly" 
Write-Host "c. Make a change and click 'Save Changes'"
Write-Host "Expected behavior: Should return to the template details page"

# Verify that Cancel button works
Write-Host "`n4. Testing Cancel button" -ForegroundColor Yellow
Write-Host "Steps:"
Write-Host "a. Go to http://localhost:5174/assessments/templates/1"
Write-Host "b. Click 'Edit' for any question" 
Write-Host "c. Click 'Cancel'"
Write-Host "Expected behavior: Should return to the template details page"

Write-Host "`nTest Instructions" -ForegroundColor Green
Write-Host "1. Run through each test scenario manually"
Write-Host "2. Verify each navigation flow works as expected"
Write-Host "3. Note any issues or unexpected behavior"
