@echo off
rem Step 3 dev harness only - prints parse stats to this window.
rem Step 6 adds run.bat to launch the Streamlit app in the browser.
setlocal

set "HERE=%~dp0"
set "PY_SPOTIFY=%HERE%..\spotify-analytics\.venv\Scripts\python.exe"
set "PY_LOCAL=%HERE%.venv\Scripts\python.exe"

if exist "%PY_SPOTIFY%" (
  set "PY=%PY_SPOTIFY%"
) else if exist "%PY_LOCAL%" (
  set "PY=%PY_LOCAL%"
) else (
  echo [ERROR] No Python runtime found.
  echo Tried:
  echo   %PY_SPOTIFY%
  echo   %PY_LOCAL%
  echo.
  echo Create one with:
  echo   py -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  exit /b 1
)

echo Running parse.py with:
echo   %PY%
"%PY%" "%HERE%parse.py"

echo.
echo Press any key to close...
pause >nul
