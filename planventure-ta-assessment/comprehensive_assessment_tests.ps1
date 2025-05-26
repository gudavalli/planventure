# Comprehensive Assessment API Tests
# This script tests all assessment-related endpoints after the 500 error fix

$baseUrl = "http://127.0.0.1:5001"
$testResults = @()

function Test-Endpoint {
    param(
        [string]$TestName,
        [string]$Method,
        [string]$Endpoint,
        [string]$Body = $null,
        [int]$ExpectedStatus,
        [string]$Description
    )
    
    Write-Host "`n=== $TestName ===" -ForegroundColor Cyan
    Write-Host "Testing: $Method $Endpoint" -ForegroundColor Yellow
    Write-Host "Expected Status: $ExpectedStatus" -ForegroundColor Yellow
    Write-Host "Description: $Description" -ForegroundColor Gray
    
    try {
        $headers = @{
            'Content-Type' = 'application/json'
        }
        
        $response = if ($Body) {
            Invoke-WebRequest -Uri "$baseUrl$Endpoint" -Method $Method -Body $Body -Headers $headers -UseBasicParsing
        } else {
            Invoke-WebRequest -Uri "$baseUrl$Endpoint" -Method $Method -Headers $headers -UseBasicParsing
        }
        
        $actualStatus = $response.StatusCode
        $success = $actualStatus -eq $ExpectedStatus
        
        Write-Host "Actual Status: $actualStatus" -ForegroundColor $(if($success) { "Green" } else { "Red" })
        
        if ($success) {
            Write-Host "✅ PASS" -ForegroundColor Green
        } else {
            Write-Host "❌ FAIL" -ForegroundColor Red
        }
        
        $testResults += [PSCustomObject]@{
            TestName = $TestName
            Method = $Method
            Endpoint = $Endpoint
            Expected = $ExpectedStatus
            Actual = $actualStatus
            Status = if($success) { "PASS" } else { "FAIL" }
            Description = $Description
        }
        
        # Show response content for some key tests
        if ($TestName -like "*List*" -or $TestName -like "*Create*" -or $actualStatus -ne $ExpectedStatus) {
            $content = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($content) {
                Write-Host "Response Preview:" -ForegroundColor Magenta
                if ($content.PSObject.Properties['templates']) {
                    Write-Host "  Templates found: $($content.templates.Count)" -ForegroundColor White
                } elseif ($content.PSObject.Properties['assessments']) {
                    Write-Host "  Assessments found: $($content.assessments.Count)" -ForegroundColor White
                } elseif ($content.PSObject.Properties['questions']) {
                    Write-Host "  Questions found: $($content.questions.Count)" -ForegroundColor White
                } elseif ($content.PSObject.Properties['id']) {
                    Write-Host "  Created ID: $($content.id)" -ForegroundColor White
                } elseif ($content.PSObject.Properties['error']) {
                    Write-Host "  Error: $($content.error)" -ForegroundColor Red
                }
            }
        }
        
    } catch {
        $actualStatus = $_.Exception.Response.StatusCode.value__
        $success = $actualStatus -eq $ExpectedStatus
        
        Write-Host "Actual Status: $actualStatus (via exception)" -ForegroundColor $(if($success) { "Green" } else { "Red" })
        
        if ($success) {
            Write-Host "✅ PASS (Expected error)" -ForegroundColor Green
        } else {
            Write-Host "❌ FAIL (Unexpected error)" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        $testResults += [PSCustomObject]@{
            TestName = $TestName
            Method = $Method
            Endpoint = $Endpoint
            Expected = $ExpectedStatus
            Actual = $actualStatus
            Status = if($success) { "PASS" } else { "FAIL" }
            Description = $Description
        }
    }
}

Write-Host "🚀 Starting Comprehensive Assessment API Tests" -ForegroundColor Green
Write-Host "Testing PlanVenture HR Assessment System after 500 error fix" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

# Test 1: List Templates (Core functionality)
Test-Endpoint -TestName "Template_List" -Method "GET" -Endpoint "/api/templates" -ExpectedStatus 200 -Description "Get all available templates"

# Test 2: List Assessments (Core functionality)
Test-Endpoint -TestName "Assessment_List" -Method "GET" -Endpoint "/api/assessments" -ExpectedStatus 200 -Description "Get all assessments"

# Test 3: Get Valid Template Details (Fixed 500 error scenario)
Test-Endpoint -TestName "Template_Valid_Details" -Method "GET" -Endpoint "/api/templates/2" -ExpectedStatus 200 -Description "Get details for valid template"

# Test 4: Get Invalid Template Details (Previously returned 500, now should return 404)
Test-Endpoint -TestName "Template_Invalid_Details" -Method "GET" -Endpoint "/api/templates/999999" -ExpectedStatus 404 -Description "Get details for non-existent template (was 500, now 404)"

# Test 5: Get Valid Template Analytics
Test-Endpoint -TestName "Template_Valid_Analytics" -Method "GET" -Endpoint "/api/templates/2/analytics" -ExpectedStatus 200 -Description "Get analytics for valid template"

# Test 6: Get Invalid Template Analytics (Should return 404)
Test-Endpoint -TestName "Template_Invalid_Analytics" -Method "GET" -Endpoint "/api/templates/999999/analytics" -ExpectedStatus 404 -Description "Get analytics for non-existent template"

# Test 7: Create New Template
$newTemplateJson = @{
    name = "Test API Template $(Get-Date -Format 'yyyyMMdd_HHmmss')"
    description = "Template created during API testing"
    time_limit = 1800
    percentage = 100.0
} | ConvertTo-Json

Test-Endpoint -TestName "Template_Create" -Method "POST" -Endpoint "/api/templates" -Body $newTemplateJson -ExpectedStatus 201 -Description "Create new template"

# Test 8: Create New Assessment (need to get a valid template ID first)
$templatesResponse = Invoke-WebRequest -Uri "$baseUrl/api/templates" -Method GET -Headers @{'Content-Type'='application/json'} -UseBasicParsing
$templates = ($templatesResponse.Content | ConvertFrom-Json).templates
$validTemplateId = $templates[0].id

$newAssessmentJson = @{
    template_id = $validTemplateId
    user_email = "test.assessment@example.com"
} | ConvertTo-Json

Test-Endpoint -TestName "Assessment_Create" -Method "POST" -Endpoint "/api/assessments" -Body $newAssessmentJson -ExpectedStatus 201 -Description "Create new assessment"

# Test 9: Get Valid Assessment Questions
$assessmentsResponse = Invoke-WebRequest -Uri "$baseUrl/api/assessments" -Method GET -Headers @{'Content-Type'='application/json'} -UseBasicParsing
$assessments = ($assessmentsResponse.Content | ConvertFrom-Json).assessments
$validAssessmentId = $assessments[0].id

Test-Endpoint -TestName "Assessment_Valid_Questions" -Method "GET" -Endpoint "/api/assessments/$validAssessmentId/questions" -ExpectedStatus 200 -Description "Get questions for valid assessment"

# Test 10: Get Invalid Assessment Questions (Should return 404)
Test-Endpoint -TestName "Assessment_Invalid_Questions" -Method "GET" -Endpoint "/api/assessments/999999/questions" -ExpectedStatus 404 -Description "Get questions for non-existent assessment"

# Test 11: Start Valid Assessment
Test-Endpoint -TestName "Assessment_Valid_Start" -Method "POST" -Endpoint "/api/assessments/$validAssessmentId/start" -ExpectedStatus 200 -Description "Start valid assessment"

# Test 12: Start Invalid Assessment (Should return error)
Test-Endpoint -TestName "Assessment_Invalid_Start" -Method "POST" -Endpoint "/api/assessments/999999/start" -ExpectedStatus 400 -Description "Start non-existent assessment"

# Test 13: Submit Answer to Valid Assessment
$submitAnswerJson = @{
    question_id = 1
    answer = "Test answer for API testing"
} | ConvertTo-Json

Test-Endpoint -TestName "Assessment_Valid_Submit" -Method "POST" -Endpoint "/api/assessments/$validAssessmentId/submit-answer" -Body $submitAnswerJson -ExpectedStatus 200 -Description "Submit answer to valid assessment"

# Test 14: Submit Answer to Invalid Assessment (Should return 404)
Test-Endpoint -TestName "Assessment_Invalid_Submit" -Method "POST" -Endpoint "/api/assessments/999999/submit-answer" -Body $submitAnswerJson -ExpectedStatus 404 -Description "Submit answer to non-existent assessment"

# Test 15: Add Questions to Valid Template
$addQuestionsJson = @{
    question_ids = @(1, 2)
} | ConvertTo-Json

Test-Endpoint -TestName "Template_Valid_Add_Questions" -Method "POST" -Endpoint "/api/templates/$validTemplateId/questions" -Body $addQuestionsJson -ExpectedStatus 200 -Description "Add questions to valid template"

# Test 16: Add Questions to Invalid Template (Should return error)
Test-Endpoint -TestName "Template_Invalid_Add_Questions" -Method "POST" -Endpoint "/api/templates/999999/questions" -Body $addQuestionsJson -ExpectedStatus 400 -Description "Add questions to non-existent template"

# Generate Test Report
Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "📊 COMPREHENSIVE TEST RESULTS SUMMARY" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green

$passCount = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$totalTests = $testResults.Count

Write-Host "`nOverall Results:" -ForegroundColor White
Write-Host "✅ PASSED: $passCount/$totalTests tests" -ForegroundColor Green
Write-Host "❌ FAILED: $failCount/$totalTests tests" -ForegroundColor $(if($failCount -eq 0) { "Green" } else { "Red" })

if ($failCount -gt 0) {
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    $testResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  - $($_.TestName): Expected $($_.Expected), Got $($_.Actual)" -ForegroundColor Red
    }
}

Write-Host "`nDetailed Results:" -ForegroundColor White
$testResults | Format-Table -AutoSize

# Key Findings Summary
Write-Host "`n🔍 KEY FINDINGS:" -ForegroundColor Yellow
Write-Host "1. 500 Error Fix Status: " -NoNewline
$errorFixTests = $testResults | Where-Object { $_.TestName -like "*Invalid*" -and $_.Expected -eq 404 }
$errorFixPassed = ($errorFixTests | Where-Object { $_.Status -eq "PASS" }).Count
if ($errorFixPassed -eq $errorFixTests.Count) {
    Write-Host "✅ FIXED - All invalid resource requests now return 404 instead of 500" -ForegroundColor Green
} else {
    Write-Host "❌ ISSUES REMAINING - Some invalid requests still not returning proper 404" -ForegroundColor Red
}

Write-Host "2. Core Functionality: " -NoNewline
$coreTests = $testResults | Where-Object { $_.TestName -like "*List*" -or $_.TestName -like "*Create*" -or $_.TestName -like "*Valid*" }
$corePassed = ($coreTests | Where-Object { $_.Status -eq "PASS" }).Count
if ($corePassed -eq $coreTests.Count) {
    Write-Host "✅ WORKING - All core features operational" -ForegroundColor Green
} else {
    Write-Host "❌ ISSUES - Some core features not working properly" -ForegroundColor Red
}

Write-Host "3. Error Handling: " -NoNewline
$errorTests = $testResults | Where-Object { $_.Expected -ge 400 }
$errorPassed = ($errorTests | Where-Object { $_.Status -eq "PASS" }).Count
if ($errorPassed -eq $errorTests.Count) {
    Write-Host "✅ PROPER - Error responses returning correct status codes" -ForegroundColor Green
} else {
    Write-Host "❌ INCONSISTENT - Some error responses not following expected patterns" -ForegroundColor Red
}

$successRate = [math]::Round(($passCount / $totalTests) * 100, 1)
Write-Host "`n🎯 SUCCESS RATE: $successRate%" -ForegroundColor $(if($successRate -ge 95) { "Green" } elseif($successRate -ge 80) { "Yellow" } else { "Red" })

Write-Host "`n✅ Assessment testing completed!" -ForegroundColor Green
Write-Host "Report saved to test results above." -ForegroundColor Gray
