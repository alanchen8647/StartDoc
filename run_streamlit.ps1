# DocuBot Streamlit App Launcher (PowerShell version)
# Run with: .\run_streamlit.ps1

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    DocuBot Streamlit App Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "[2/3] Checking dependencies..." -ForegroundColor Green
python -m pip install -q streamlit google-genai python-dotenv nltk 2>$null

# Show startup info
Write-Host "[3/3] Starting Streamlit app..." -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    🚀 DocuBot is starting..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "    📍 Local URL:   http://localhost:8501" -ForegroundColor Yellow
Write-Host "    📍 Network URL: http://192.168.1.x:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "    ✓ App should open in your browser automatically" -ForegroundColor Green
Write-Host "    ✓ If not, paste the URL above into your browser" -ForegroundColor Green
Write-Host "    ✓ Press Ctrl+C to stop the server" -ForegroundColor Green
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Run Streamlit
python -m streamlit run app.py --logger.level=error

Write-Host ""
Write-Host "Press Enter to exit"
Read-Host
