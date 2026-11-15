@echo off
REM Start DocuBot Streamlit app
REM This script activates the virtual environment and runs the Streamlit app

setlocal enabledelayedexpansion

echo ============================================================
echo    DocuBot Streamlit App Launcher
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [2/3] Checking dependencies...
python -m pip install -q streamlit google-genai python-dotenv nltk 2>nul

echo [3/3] Starting Streamlit app...
echo.
echo ============================================================
echo    🚀 DocuBot is starting...
echo ============================================================
echo.
echo    📍 Local URL:   http://localhost:8501
echo    📍 Network URL: http://192.168.1.x:8501
echo.
echo    ✓ App should open in your browser automatically
echo    ✓ If not, paste the URL above into your browser
echo    ✓ Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

REM Run Streamlit using Python module (more reliable than direct command)
python -m streamlit run app.py --logger.level=error

pause
