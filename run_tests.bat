@echo off
REM Quick Start Script for Conference Room Booking System Tests (Windows)

echo ================================================
echo Conference Room Booking System - Test Runner
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [WARNING] Virtual environment not found. Creating one...
    python -m venv .venv
    echo [INFO] Virtual environment created.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo [WARNING] Installing dependencies...
    pip install -r requirements.txt
    echo [INFO] Dependencies installed.
)

REM Main menu
echo.
echo Select test option:
echo 1^) Run all tests
echo 2^) Run tests with coverage
echo 3^) Run specific user story tests
echo 4^) Run code quality checks
echo 5^) Run security checks
echo 6^) Generate coverage report ^(HTML^)
echo 7^) Quick smoke tests
echo 8^) Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" (
    echo [INFO] Running all tests...
    pytest -v
) else if "%choice%"=="2" (
    echo [INFO] Running tests with coverage...
    pytest -v --cov=app --cov-report=term-missing
) else if "%choice%"=="3" (
    echo.
    echo Select User Story to test:
    echo 1^) US-01: View Available Rooms
    echo 2^) US-02: Book Conference Room
    echo 3^) US-03: Automatic Confirmation
    echo 4^) US-04: Specify Room Requirements
    echo 5^) US-05: Cancel/Modify Booking
    echo 6^) US-06: User Authentication
    echo 7^) US-08: Booking Reminders
    echo.
    set /p us_choice="Enter choice (1-7): "

    if "!us_choice!"=="1" pytest -m us01 -v
    if "!us_choice!"=="2" pytest -m us02 -v
    if "!us_choice!"=="3" pytest -m us03 -v
    if "!us_choice!"=="4" pytest -m us04 -v
    if "!us_choice!"=="5" pytest -m us05 -v
    if "!us_choice!"=="6" pytest -m us06 -v
    if "!us_choice!"=="7" pytest -m us08 -v
) else if "%choice%"=="4" (
    echo [INFO] Running code quality checks...
    echo.
    echo [INFO] 1. Black ^(Code Formatting^)...
    black --check .
    echo.
    echo [INFO] 2. Flake8 ^(Linting^)...
    flake8 . --count --statistics
    echo.
    echo [INFO] 3. Pylint ^(Static Analysis^)...
    pylint app.py --disable=all --enable=E,F
) else if "%choice%"=="5" (
    echo [INFO] Running security checks...
    echo.
    echo [INFO] 1. Bandit ^(Security Scanner^)...
    bandit -r . -ll
    echo.
    echo [INFO] 2. Safety ^(Dependency Check^)...
    safety check
    echo.
    echo [INFO] 3. pip-audit...
    pip-audit
) else if "%choice%"=="6" (
    echo [INFO] Generating HTML coverage report...
    pytest --cov=app --cov-report=html
    echo [INFO] Coverage report generated in htmlcov\index.html
    start htmlcov\index.html
) else if "%choice%"=="7" (
    echo [INFO] Running quick smoke tests...
    pytest -m smoke -v --tb=short
) else if "%choice%"=="8" (
    echo [INFO] Exiting...
    exit /b 0
) else (
    echo [ERROR] Invalid choice
    exit /b 1
)

echo.
echo [INFO] Test run completed!
echo.
pause