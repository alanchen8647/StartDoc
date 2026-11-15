#!/bin/bash
# DocuBot Streamlit App Launcher (Mac/Linux version)
# Usage: chmod +x run_streamlit.sh && ./run_streamlit.sh

echo "============================================================"
echo "    DocuBot Streamlit App Launcher"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    read -p "Press Enter to exit"
    exit 1
fi

# Activate virtual environment
echo "[1/3] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[2/3] Checking dependencies..."
pip install -q streamlit google-genai python-dotenv nltk 2>/dev/null

# Show startup info
echo "[3/3] Starting Streamlit app..."
echo ""
echo "============================================================"
echo "    🚀 DocuBot is starting..."
echo "============================================================"
echo ""
echo "    📍 Local URL:   http://localhost:8501"
echo "    📍 Network URL: http://192.168.x.x:8501"
echo ""
echo "    ✓ App should open in your browser automatically"
echo "    ✓ If not, paste the URL above into your browser"
echo "    ✓ Press Ctrl+C to stop the server"
echo ""
echo "============================================================"
echo ""

# Run Streamlit
python -m streamlit run app.py --logger.level=error

echo ""
echo "Press Enter to exit"
read
