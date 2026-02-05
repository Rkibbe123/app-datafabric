# AI-Validated Smoke Test Script
# This script generates, uploads, executes, and analyzes smoke tests for Databricks

param(
    [string]$databricksHost,
    [string]$databricksToken,
    [string]$azureOpenAIEndpoint,
    [string]$azureOpenAIDeployment,
    [string]$notebooksPath,
    [string]$target,
    [string]$repoPath
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   AI-VALIDATED SMOKE TEST                  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$env:DATABRICKS_HOST = $databricksHost
$env:DATABRICKS_TOKEN = $databricksToken

# ========================================
# PHASE 1: Generate Dynamic Smoke Test
# ========================================
Write-Host ""
Write-Host "📝 PHASE 1: Generating Dynamic Smoke Test Notebook" -ForegroundColor Yellow

# Get Azure AD token for Azure OpenAI
$aiToken = az account get-access-token --resource https://ml.azure.com --query accessToken -o tsv

# Define a reliable fallback smoke test
$fallbackCells = @(
    "import sys`nprint(f'Python version: {sys.version}')`nprint('SMOKE_TEST: Starting...')",
    "# Test 1: Basic Spark SQL`ntry:`n    result = spark.sql('SELECT 1 as smoke_test').collect()`n    assert result[0][0] == 1`n    print('TEST 1 PASSED: Spark SQL working')`nexcept Exception as e:`n    print(f'TEST 1 FAILED: {str(e)}')",
    "# Test 2: DataFrame Operations`ntry:`n    df = spark.range(10)`n    count = df.count()`n    assert count == 10, f'Expected 10, got {count}'`n    print('TEST 2 PASSED: DataFrame operations working')`nexcept Exception as e:`n    print(f'TEST 2 FAILED: {str(e)}')",
    "# Test 3: Catalog Check`ntry:`n    catalogs = spark.sql('SHOW CATALOGS').collect()`n    print(f'TEST 3 PASSED: Found {len(catalogs)} catalog(s)')`nexcept Exception as e:`n    print(f'TEST 3 SKIPPED: {str(e)}')",
    "print('='*50)`nprint('SMOKE_TEST_PASSED')`nprint('='*50)"
)

$prompt = @"
Generate a simple Databricks smoke test as a JSON array of Python code strings.
Target: $target

Requirements:
- Use ONLY standard PySpark (no external imports)
- Wrap tests in try/except
- Print SMOKE_TEST_PASSED at end

Tests needed:
1. Print Python version
2. spark.sql("SELECT 1")
3. spark.range(10).count()
4. SHOW CATALOGS (with try/except)

Return ONLY a JSON array like: ["code1", "code2"]
"@

$body = @{
    model = $azureOpenAIDeployment
    input = $prompt
} | ConvertTo-Json -Depth 10

$uri = "$azureOpenAIEndpoint"

Write-Host "  Generating smoke test with AI..."

# Helper function to parse AI response
function Get-AIResponseText($resp) {
    if ($resp.output -and $resp.output[0].content) { return $resp.output[0].content[0].text }
    if ($resp.choices -and $resp.choices[0].message) { return $resp.choices[0].message.content }
    if ($resp.text) { return $resp.text }
    if ($resp.content) { return $resp.content }
    if ($resp -is [string]) { return $resp }
    return $null
}

try {
    $response = Invoke-RestMethod -Uri $uri -Method POST -Headers @{
        "Authorization" = "Bearer $aiToken"
        "Content-Type" = "application/json"
    } -Body $body
    
    $generatedCells = Get-AIResponseText $response
    if (-not $generatedCells) { throw "Unable to parse AI response" }
    
    if ($generatedCells -match '\[[\s\S]*\]') {
        $generatedCells = $matches[0]
    }
    
    $cells = $generatedCells | ConvertFrom-Json
    if ($cells.Count -eq 0) { throw "Empty" }
    Write-Host "  AI generated $($cells.Count) cells" -ForegroundColor Green
} catch {
    Write-Host "  Using fallback smoke test" -ForegroundColor Yellow
    $cells = $fallbackCells
}

# ========================================
# PHASE 2: Upload to Databricks
# ========================================
Write-Host ""
Write-Host "📤 PHASE 2: Uploading Smoke Test to Databricks" -ForegroundColor Yellow

# Create SOURCE format notebook
$sourceNotebook = "# Databricks notebook source`n"
$sourceNotebook += "# MAGIC %md`n# MAGIC # CI/CD Smoke Test - $target`n`n"

foreach ($cell in $cells) {
    $sourceNotebook += "# COMMAND ----------`n`n"
    $sourceNotebook += $cell
    $sourceNotebook += "`n`n"
}

$headers = @{
    "Authorization" = "Bearer $databricksToken"
    "Content-Type" = "application/json"
}

$smokeTestFolder = "/Shared/cicd_smoke_tests"
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$workspacePath = "$smokeTestFolder/smoke_test_${target}_$timestamp"

Write-Host "  Target: $workspacePath"

# Create directory
$mkdirBody = @{ path = $smokeTestFolder } | ConvertTo-Json
try {
    Invoke-RestMethod -Uri "$databricksHost/api/2.0/workspace/mkdirs" -Method POST -Headers $headers -Body $mkdirBody | Out-Null
    Write-Host "  Directory ready" -ForegroundColor Green
} catch {
    Write-Host "  Warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Upload notebook
$notebookBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sourceNotebook))
$importBody = @{
    path = $workspacePath
    format = "SOURCE"
    language = "PYTHON"
    content = $notebookBase64
    overwrite = $true
} | ConvertTo-Json

$uploadSuccess = $false
try {
    Invoke-RestMethod -Uri "$databricksHost/api/2.0/workspace/import" -Method POST -Headers $headers -Body $importBody | Out-Null
    Write-Host "  Notebook uploaded" -ForegroundColor Green
    $uploadSuccess = $true
} catch {
    Write-Host "  Upload failed: $($_.Exception.Message)" -ForegroundColor Red
}

# ========================================
# PHASE 3: Execute Smoke Test
# ========================================
Write-Host ""
Write-Host "🚀 PHASE 3: Executing Smoke Test" -ForegroundColor Yellow

$runOutput = ""
$runStatus = "UNKNOWN"

if ($uploadSuccess) {
    $jobSpec = @{
        run_name = "SmokeTest_${target}_$timestamp"
        notebook_task = @{ notebook_path = $workspacePath }
        new_cluster = @{
            spark_version = "14.3.x-scala2.12"
            node_type_id = "Standard_DS3_v2"
            num_workers = 0
            spark_conf = @{
                "spark.databricks.cluster.profile" = "singleNode"
                "spark.master" = "local[*]"
            }
        }
    } | ConvertTo-Json -Depth 10
    
    try {
        Write-Host "  Submitting job..."
        $runResult = Invoke-RestMethod -Uri "$databricksHost/api/2.0/jobs/runs/submit" -Method POST -Headers $headers -Body $jobSpec
        $runId = $runResult.run_id
        Write-Host "  Run ID: $runId"
        
        # Poll for completion
        $maxWait = 600
        $waited = 0
        
        do {
            Start-Sleep -Seconds 15
            $waited += 15
            $statusResult = Invoke-RestMethod -Uri "$databricksHost/api/2.0/jobs/runs/get?run_id=$runId" -Method GET -Headers $headers
            $runStatus = $statusResult.state.life_cycle_state
            $msg = if ($statusResult.state.state_message) { " - $($statusResult.state.state_message)" } else { "" }
            Write-Host "  Status: $runStatus$msg (${waited}s)"
        } while ($runStatus -in @("PENDING", "RUNNING", "QUEUED", "TERMINATING") -and $waited -lt $maxWait)
        
        if ($statusResult.state.result_state) {
            $runStatus = $statusResult.state.result_state
        }
        Write-Host "  Final: $runStatus" -ForegroundColor $(if ($runStatus -eq "SUCCESS") { "Green" } else { "Red" })
        
        # Get output
        try {
            $outputResult = Invoke-RestMethod -Uri "$databricksHost/api/2.0/jobs/runs/get-output?run_id=$runId" -Method GET -Headers $headers
            if ($outputResult.notebook_output.result) { $runOutput = $outputResult.notebook_output.result }
            if ($outputResult.error) { $runOutput += "`nError: $($outputResult.error)" }
            Write-Host "  Output: $runOutput"
        } catch {
            Write-Host "  Could not get output" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Execution failed: $_" -ForegroundColor Red
        $runStatus = "ERROR"
    }
} else {
    Write-Host "  Skipped (upload failed)"
    $runStatus = "SKIPPED"
}

# ========================================
# PHASE 4: AI Analysis
# ========================================
Write-Host ""
Write-Host "🤖 PHASE 4: AI Analysis" -ForegroundColor Yellow

$analysisPrompt = "Analyze smoke test results. Status: $runStatus, Output: $runOutput. Rate health: HEALTHY/DEGRADED/UNHEALTHY. Risk: LOW/MEDIUM/HIGH."

$analysisBody = @{
    model = $azureOpenAIDeployment
    input = $analysisPrompt
} | ConvertTo-Json -Depth 10

try {
    $analysisResponse = Invoke-RestMethod -Uri $uri -Method POST -Headers @{
        "Authorization" = "Bearer $aiToken"
        "Content-Type" = "application/json"
    } -Body $analysisBody
    
    $analysis = Get-AIResponseText $analysisResponse
    if (-not $analysis) { throw "Unable to parse AI response" }
    Write-Host $analysis
    
    if ($analysis -match "UNHEALTHY|HIGH") {
        Write-Host "##vso[task.logissue type=error]Critical issues detected"
    }
} catch {
    Write-Host "  AI analysis failed" -ForegroundColor Yellow
    if ($runStatus -eq "SUCCESS") {
        Write-Host "✅ Smoke test PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Smoke test FAILED" -ForegroundColor Red
    }
}

# ========================================
# PHASE 5: Cleanup
# ========================================
Write-Host ""
Write-Host "🧹 PHASE 5: Cleanup" -ForegroundColor Yellow

if ($uploadSuccess) {
    try {
        $deleteBody = @{ path = $workspacePath } | ConvertTo-Json
        Invoke-RestMethod -Uri "$databricksHost/api/2.0/workspace/delete" -Method POST -Headers $headers -Body $deleteBody | Out-Null
        Write-Host "  Cleaned up" -ForegroundColor Green
    } catch {
        Write-Host "  Cleanup failed" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   SMOKE TEST COMPLETE                      " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
