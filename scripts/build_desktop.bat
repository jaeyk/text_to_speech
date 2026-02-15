@echo off
setlocal

cd /d "%~dp0\.."

set "PYTHON_EXE="
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  set "PYTHON_EXE=py"
) else (
  where python >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "PYTHON_EXE=python"
  )
)

if "%PYTHON_EXE%"=="" (
  echo Error: Python 3.10+ is required.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  %PYTHON_EXE% -m venv .venv
)

set "VENV_PY=.venv\Scripts\python.exe"
"%VENV_PY%" -m pip install --upgrade pip
if not %ERRORLEVEL%==0 exit /b %ERRORLEVEL%

"%VENV_PY%" -m pip install -r requirements.txt pyinstaller
if not %ERRORLEVEL%==0 exit /b %ERRORLEVEL%

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --name PracticeTalk ^
  --windowed ^
  --add-data "static;static" ^
  --collect-all edge_tts ^
  desktop_launcher.py
if not %ERRORLEVEL%==0 exit /b %ERRORLEVEL%

echo Build complete: dist\PracticeTalk.exe
endlocal
