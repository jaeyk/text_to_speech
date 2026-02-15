@echo off
setlocal

cd /d "%~dp0\.."

call scripts\build_desktop.bat
if not %ERRORLEVEL%==0 exit /b %ERRORLEVEL%

set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
  set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
  set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%ISCC_PATH%"=="" (
  where iscc >nul 2>nul
  if %ERRORLEVEL%==0 (
    set "ISCC_PATH=iscc"
  )
)

if "%ISCC_PATH%"=="" (
  echo Error: Inno Setup is not installed. Install from https://jrsoftware.org/isdl.php
  exit /b 1
)

"%ISCC_PATH%" installers\windows\practicetalk.iss
if not %ERRORLEVEL%==0 exit /b %ERRORLEVEL%

echo Installer build complete: dist\PracticeTalk-Setup.exe
endlocal
