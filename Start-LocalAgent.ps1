# Rebuild and run the Managed Deep Agent locally on Windows.
# Stop any existing server with Ctrl+C before running this script.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$projectVenv = Join-Path $projectRoot ".venv"
$activateScript = Join-Path $projectVenv "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    throw "Project virtual environment not found. Recreate it before starting the agent."
}

Push-Location $projectRoot
try {
    & $activateScript
    & mda build .

    $buildDirectory = Join-Path $projectRoot ".mda\build"
    Push-Location $buildDirectory
    try {
        & uv sync
        & ".\.venv\Scripts\langgraph.exe" dev --allow-blocking --no-browser
    }
    finally {
        Pop-Location
    }
}
finally {
    Pop-Location
}
