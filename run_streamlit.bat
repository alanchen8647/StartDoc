@echo off
REM Start DocuBot Streamlit app

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Streamlit app...
echo.
echo 🚀 DocuBot is starting at http://localhost:8501
echo Press Ctrl+C to stop
echo.

streamlit run app.py

pause
