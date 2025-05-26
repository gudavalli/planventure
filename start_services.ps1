# PlanVenture Application Startup Script
Write-Host "Starting PlanVenture Application Services..." -ForegroundColor Green

# Function to start a service in a new window
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Path,
        [string]$Command,
        [int]$Port
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Yellow
    
    # Start the service in a new PowerShell window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Path'; $Command" -WindowStyle Normal
    
    # Wait a moment for the service to start
    Start-Sleep -Seconds 3
    
    # Check if the port is in use
    $portCheck = netstat -ano | findstr ":$Port"
    if ($portCheck) {
        Write-Host "$ServiceName started successfully on port $Port" -ForegroundColor Green
    } else {
        Write-Host "Warning: $ServiceName may not have started on port $Port" -ForegroundColor Red
    }
}

# Start Assessment Service (Port 5001)
Start-Service -ServiceName "Assessment Service" -Path "c:\Users\sreen\learning\copilot-agent\planventure\planventure-ta-assessment" -Command "python app.py" -Port 5001

# Start Account Service (Port 5000)
Start-Service -ServiceName "Account Service" -Path "c:\Users\sreen\learning\copilot-agent\planventure\planventure-account" -Command "python app.py" -Port 5000

# Start Web Application (Port 5173 - Vite default)
Write-Host "Starting Web Application..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\sreen\learning\copilot-agent\planventure\planventure-web'; npm run dev" -WindowStyle Normal

Write-Host "`nAll services starting up..." -ForegroundColor Green
Write-Host "Assessment Service: http://localhost:5001" -ForegroundColor Cyan
Write-Host "Account Service: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Web Application: http://localhost:5173" -ForegroundColor Cyan

Write-Host "`nPress any key to check service status..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Check all services
Write-Host "`nChecking service status..." -ForegroundColor Green
$ports = @(5000, 5001, 5173)
foreach ($port in $ports) {
    $portCheck = netstat -ano | findstr ":$port"
    if ($portCheck) {
        Write-Host "Port $port is active" -ForegroundColor Green
    } else {
        Write-Host "Port $port is not active" -ForegroundColor Red
    }
}

Write-Host "`nStartup complete! You can now test the application." -ForegroundColor Green
