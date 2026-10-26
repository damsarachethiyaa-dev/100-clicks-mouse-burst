@echo off
:: Batch Got Admin Check
NET SESSION >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    goto :run
) ELSE (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~dp0Start_100Clicks.bat' -Verb RunAs"
    exit /b
)

:run
cd /d "%~dp0"
call Start_100Clicks.bat
