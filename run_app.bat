@echo off
echo ========================================================
echo Starting ATS Resume Scorer (Backend + Streamlit Frontend)
echo ========================================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if exist "venv\Scripts\activate.bat" (
    echo [Environment] Found virtual environment in venv.
    start "ATS Scorer - FastAPI Backend" cmd /k "call venv\Scripts\activate.bat && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
    timeout /t 4 /nobreak >nul
    start "ATS Scorer - Streamlit Frontend" cmd /k "call venv\Scripts\activate.bat && streamlit run frontend/app.py --server.port 8501"
) else (
    echo [Environment] Using system Python.
    start "ATS Scorer - FastAPI Backend" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
    timeout /t 4 /nobreak >nul
    start "ATS Scorer - Streamlit Frontend" cmd /k "python -m streamlit run frontend/app.py --server.port 8501"
)

echo.
echo Both services are starting!
echo Backend API : http://localhost:8000
echo API Docs    : http://localhost:8000/docs
echo Web UI      : http://localhost:8501
echo ========================================================
