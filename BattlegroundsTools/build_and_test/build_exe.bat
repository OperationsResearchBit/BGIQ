@echo off
setlocal
title Build bgtools.exe

rem Builds a single-file bgtools.exe with PyInstaller.
rem Run it from anywhere; it works from the repo root.
rem Output: build_and_test\release\bgtools.exe   (work files: build_and_test\build\)

cd /d "%~dp0.." || (
    echo Could not find the repo root.
    pause
    exit /b 1
)

set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY (
    echo Python was not found. Install Python 3 from python.org and tick "Add Python to PATH".
    pause
    exit /b 1
)

%PY% -m PyInstaller --version >nul 2>nul || (
    echo PyInstaller is not installed. Run:  %PY% -m pip install pyinstaller
    pause
    exit /b 1
)

%PY% -m PyInstaller --noconfirm --onefile --name bgtools ^
    --paths . ^
    --workpath build_and_test\build ^
    --distpath build_and_test\release ^
    --specpath build_and_test\build ^
    bgtools\__main__.py || (
    echo Build failed.
    pause
    exit /b 1
)

rem AGPL-3.0: ship the license (and point people at the matching source) with the exe.
if exist docs\LICENSE copy /y docs\LICENSE build_and_test\release\LICENSE >nul
if exist README.md copy /y README.md build_and_test\release\README.md >nul
if not exist build_and_test\release\data mkdir build_and_test\release\data
copy /y data\triple_targets.txt build_and_test\release\data\triple_targets.txt >nul

echo.
echo Done: build_and_test\release\bgtools.exe
pause
