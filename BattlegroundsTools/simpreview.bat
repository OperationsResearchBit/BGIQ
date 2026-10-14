@echo off
setlocal
title Battlegrounds odds
chcp 65001 >nul
rem Shows the fight odds (win / tie / loss) from your real game.
rem   simpreview.bat                    live: follows your newest Power.log while you play (Ctrl+C to stop)
rem   simpreview.bat PATH\Power.log      the last fight of a saved log, then exit (you can drag the file onto this one)
rem   simpreview.bat --log PATH         any other simpreview option works too (--logs-dir, --debug, ...)

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

%PY% -m bgtools simpreview %ARGS%
if errorlevel 1 pause
if defined REPLAY pause
