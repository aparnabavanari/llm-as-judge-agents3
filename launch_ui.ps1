# Launch the LLM Judge Agent Streamlit UI
# PowerShell script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LLM Judge Agent System - Streamlit UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found at .venv" -ForegroundColor Yellow
    Write-Host "Using system Python installation" -ForegroundColor Yellow
}

# Check if streamlit is installed
try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Streamlit not installed"
    }
} catch {
    Write-Host "Error: Streamlit is not installed" -ForegroundColor Red
    Write-Host "Please run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Check if OPENAI_API_KEY is set
if (-not $env:OPENAI_API_KEY) {
    Write-Host ""
    Write-Host "Warning: OPENAI_API_KEY environment variable is not set" -ForegroundColor Yellow
    Write-Host "Please set your API key:" -ForegroundColor Yellow
    Write-Host '  $env:OPENAI_API_KEY = "your-api-key-here"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or create a .env file with:" -ForegroundColor Yellow
    Write-Host "  OPENAI_API_KEY=your-api-key-here" -ForegroundColor Cyan
    Write-Host ""
    Read-Host -Prompt "Press Enter to continue anyway (will fail during evaluation)"
}

Write-Host ""
Write-Host "Starting Streamlit UI..." -ForegroundColor Green
Write-Host "The application will open in your browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Launch streamlit
streamlit run streamlit_app.py
