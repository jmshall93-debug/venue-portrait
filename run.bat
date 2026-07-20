@echo off
title Venue Portrait
setlocal

set "HERE=%~dp0"
cd /d "%HERE%"

set "PY_SPOTIFY=%HERE%..\spotify-analytics\.venv\Scripts\python.exe"
set "PY_LOCAL=%HERE%.venv\Scripts\python.exe"

if exist "%PY_LOCAL%" (
  set "PY=%PY_LOCAL%"
) else if exist "%PY_SPOTIFY%" (
  set "PY=%PY_SPOTIFY%"
) else (
  echo [ERROR] No Python runtime found.
  echo Create one with:
  echo   py -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

echo.
echo  Venue Portrait  ^>  http://localhost:8502
echo  Close this window to stop the app.
echo.

"%PY%" -m streamlit run app.py --server.port 8502 --server.headless false

pause
