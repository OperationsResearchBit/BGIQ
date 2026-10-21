@echo off
setlocal
title Battlegrounds buy delta
chcp 65001 >nul
rem Shows only the tavern, with how much buying each minion would change your next fight.
rem   buydelta.bat                    live: follows your newest Power.log while you play (Ctrl+C to stop)
rem   buydelta.bat PATH\Power.log      the last tavern of a saved log, then exit (you can drag the file onto this one)
rem   buydelta.bat --debug             also show the boards the numbers are based on

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

set "REPLAY="
set ARGS=%*
if not "%~1"=="" if exist "%~1" (
    set "REPLAY=1"
    set ARGS=--replay "%~1"
)

%PY% -m bgtools buydelta %ARGS%
if errorlevel 1 pause
if defined REPLAY pause
