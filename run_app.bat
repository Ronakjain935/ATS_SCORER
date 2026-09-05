@echo off
echo ========================================================
echo Starting ATS Resume Scorer (Backend + Streamlit Frontend)
echo ========================================================

start "ATS Scorer - FastAPI Backend" cmd /k ".\venv\Scripts\activate.bat && uvicorn backend.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
start "ATS Scorer - Streamlit Frontend" cmd /k ".\venv\Scripts\activate.bat && streamlit run frontend/app.py --server.port 8501"

echo.
echo Both services are starting!
echo Backend API : http://localhost:8000
echo Web UI      : http://localhost:8501
echo ========================================================
