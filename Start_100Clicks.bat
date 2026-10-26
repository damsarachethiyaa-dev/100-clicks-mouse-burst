@echo off
title 100-Clicks Mouse Burst Multiplier
color 0b
echo ========================================================
echo        100-CLICKS MOUSE BURST MULTIPLIER
echo ========================================================
echo.
echo Launching 100-Clicks Multiplier...
echo Press F6 anytime to pause/resume.
echo Press ESC for emergency stop.
echo.
cd /d "%~dp0"
C:\Python314\python.exe burst_clicker.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An issue occurred while running the script.
    pause
)
