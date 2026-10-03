@echo off
setlocal
title Battlegrounds Tools
chcp 65001 >nul

cd /d "%~dp0bgtools" || (
    echo Could not find the bgtools folder next to this file.
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

:menu
cls
echo ==========================================
echo        BATTLEGROUNDS TOOLS
echo ==========================================
echo.
echo   1. Live tracker  (start a Battlegrounds game first)
echo   2. Browse minions  (interactive)
echo   3. Show minions for one tier
echo   4. Refresh card data  (after a game patch)
echo   5. Open README
echo   Q. Quit
echo.
echo   Tip: Ctrl+C stops the tracker. If asked "Terminate batch job",
echo   answer N to come back to this menu.
echo.
set "choice="
set /p "choice=Choose an option: "
if /i "%choice%"=="1" goto tracker
if /i "%choice%"=="2" goto browse
if /i "%choice%"=="3" goto tier
if /i "%choice%"=="4" goto refresh
if /i "%choice%"=="5" goto readme
if /i "%choice%"=="q" exit /b 0
goto menu

:tracker
cls
%PY% bgtrack.py
echo.
pause
goto menu

:browse
cls
%PY% bgminions.py -i
echo.
pause
goto menu

:tier
set "tier="
set /p "tier=Tier number (1-7): "
if "%tier%"=="" goto menu
cls
%PY% bgminions.py -t %tier%
echo.
pause
goto menu

:refresh
cls
%PY% bgminions.py --refresh >nul
echo.
echo Card data updated.
pause
goto menu

:readme
start "" "README.md"
goto menu
