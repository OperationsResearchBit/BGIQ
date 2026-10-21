@echo off
setlocal
title buy_delta preview
chcp 65001 >nul
rem Shows what buy_delta says for boards you type in. No game needed.
rem   buydeltapreview.bat                                           the example cases
rem   buydeltapreview.bat --you "3/3" --opp "4/4" --shop "2/2, 5/5"   your own boards
rem   buydeltapreview.bat --you "3/3" --turn 5 --shop "2/2, 5/5"      against typical turn-5 boards
rem Boards are atk/hp separated by commas; add taunt, shield, venom, reborn or wind after a size.

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

%PY% -m bgtools buydeltapreview %*
pause
