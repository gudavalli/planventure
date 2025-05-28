# PlanVenture Application Shutdown Script
Write-Host "Shutting down PlanVenture Application Services..." -ForegroundColor Red

# Function to stop processes by port
function Stop-ProcessByPort {
    param([int]$Port, [string]$ServiceName)
    
    Write-Host "Checking for $ServiceName on port $Port..." -ForegroundColor Yellow
    
    $connections = netstat -ano | findstr ":$Port"
    if ($connections) {
        Write-Host "Found service on port $Port" -ForegroundColor Green
        
        # Extract PIDs from netstat output
        $pids = $connections | ForEach-Object {
            if ($_ -match '\s+(\d+)\s*$') {
                $matches[1]
            }
        } | Sort-Object -Unique
        
        foreach ($procid in $pids) {
            if ($procid -and $procid -ne "0") {
                try {
                    $process = Get-Process -Id $procid -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Host "Stopping $ServiceName (PID: $procid, Process: $($process.ProcessName))" -ForegroundColor Red
                        Stop-Process -Id $procid -Force
                        Write-Host "✅ Stopped $ServiceName" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "Could not stop process $procid - it may have already stopped" -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host "No service found on port $Port" -ForegroundColor Gray
    }
}

# Stop all PlanVenture services
Write-Host "`n🔴 Stopping PlanVenture Services..." -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Red

# Stop Account Service (Port 5000)
Stop-ProcessByPort -Port 5000 -ServiceName "Account Service"

# Stop Assessment Service (Port 5001)
Stop-ProcessByPort -Port 5001 -ServiceName "Assessment Service"

# Stop Web Application (Port 5173 - Vite default)
Stop-ProcessByPort -Port 5173 -ServiceName "Web Application"

# Additional cleanup - stop any remaining Python processes that might be Flask apps
Write-Host "`n🧹 Additional Cleanup..." -ForegroundColor Yellow
$pythonProcesses = Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.StartTime -gt (Get-Date).AddHours(-2)}

if ($pythonProcesses) {
    Write-Host "Found recent Python processes that might be PlanVenture services:" -ForegroundColor Yellow
    $pythonProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), Started: $($_.StartTime)" -ForegroundColor Gray
        
        # Ask user confirmation for each process
        $response = Read-Host "Stop this Python process? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                Stop-Process -Id $_.Id -Force
                Write-Host "✅ Stopped Python process $($_.Id)" -ForegroundColor Green
            } catch {
                Write-Host "❌ Could not stop process $($_.Id)" -ForegroundColor Red
            }
        }
    }
}

# Stop any Node.js processes (for the web app)
$nodeProcesses = Get-Process | Where-Object {$_.ProcessName -eq "node" -and $_.StartTime -gt (Get-Date).AddHours(-2)}
if ($nodeProcesses) {
    Write-Host "`nFound recent Node.js processes:" -ForegroundColor Yellow
    $nodeProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id), Started: $($_.StartTime)" -ForegroundColor Gray
        
        $response = Read-Host "Stop this Node.js process? (y/N)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                Stop-Process -Id $_.Id -Force
                Write-Host "✅ Stopped Node.js process $($_.Id)" -ForegroundColor Green
            } catch {
                Write-Host "❌ Could not stop process $($_.Id)" -ForegroundColor Red
            }
        }
    }
}

# Final verification
Write-Host "`n🔍 Final Verification..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$ports = @(5000, 5001, 5173)
$anyRunning = $false

foreach ($port in $ports) {
    $portCheck = netstat -ano | findstr ":$port"
    if ($portCheck) {
        Write-Host "⚠️  Port $port is still in use" -ForegroundColor Yellow
        $anyRunning = $true
    } else {
        Write-Host "✅ Port $port is free" -ForegroundColor Green
    }
}

if (-not $anyRunning) {
    Write-Host "`n🎉 All PlanVenture services have been shut down successfully!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some services may still be running. You may need to manually stop them." -ForegroundColor Yellow
    Write-Host "Run 'netstat -ano | findstr :PORT_NUMBER' to check specific ports." -ForegroundColor Gray
}

Write-Host "`n💡 To restart services, use: .\start_services.ps1" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
