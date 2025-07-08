@echo off
REM Price Comparison Tool Setup Script for Windows
REM This script helps set up and run the price comparison tool

echo Price Comparison Tool Setup
echo =================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is required but not installed.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is required but not installed.
    pause
    exit /b 1
)

echo ✓ Python and pip are available

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo ✓ Dependencies installed

REM Create cache directory
echo Creating cache directory...
if not exist cache mkdir cache
echo ✓ Cache directory created

REM Run tests
echo Running basic tests...
python test_tool.py

echo ✓ Basic tests completed

echo.
echo Setup complete!
echo.
echo To run the application:
echo   python app.py
echo.
echo To test the tool:
echo   python test_tool.py
echo.
echo To run with Docker:
echo   docker-compose up --build
echo.
echo API will be available at: http://localhost:5000
pause
