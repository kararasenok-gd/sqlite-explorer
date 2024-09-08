@echo off
title SQLite Explorer - Install

echo Installing dependencies...
pip install rich prompt_toolkit

if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check your Python and pip installation.
    pause
    exit /b
)

echo All dependencies are installed successfully!

echo Starting SQLite Explorer...
start start.bat
