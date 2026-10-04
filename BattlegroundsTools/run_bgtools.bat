@echo off
setlocal
title Battlegrounds Tools
chcp 65001 >nul

cd /d "%~dp0" || (
    echo Could not open the folder this file is in.
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

%PY% -m bgtools %*
if errorlevel 1 pause
