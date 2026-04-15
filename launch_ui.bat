@echo off
REM Launch the LLM Judge Agent Streamlit UI

echo ========================================
echo LLM Judge Agent System - Streamlit UI
echo ========================================
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at .venv
    echo Using system Python installation
)

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Error: Streamlit is not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if OPENAI_API_KEY is set
if not defined OPENAI_API_KEY (
    echo.
    echo Warning: OPENAI_API_KEY environment variable is not set
    echo Please set your API key:
    echo   $env:OPENAI_API_KEY = "your-api-key-here"
    echo.
    echo Or create a .env file with:
    echo   OPENAI_API_KEY=your-api-key-here
    echo.
    pause
)

echo.
echo Starting Streamlit UI...
echo The application will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py

pause
