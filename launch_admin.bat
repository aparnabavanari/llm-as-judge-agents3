@echo off
REM Admin UI Launcher for Windows

echo ===============================================
echo  LLM Judge Agent System - Admin Panel
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found! Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting Admin Panel...
echo.
echo The admin panel will open in your browser at: http://localhost:8502
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run Streamlit app on port 8502 (different from main app)
streamlit run admin_app.py --server.port=8502

pause
