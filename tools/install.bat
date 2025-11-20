@echo off
REM Quick install script for japi_cli (Windows)
REM Installs using pip

echo =========================================
echo   JAPI CLI Installation Script
echo =========================================
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo Checking Python version...
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"
if %errorlevel% neq 0 (
    echo Error: Python 3.9 or higher is required
    echo Please upgrade Python and try again
    pause
    exit /b 1
)

echo Python version OK
echo.

REM Navigate to japi_cli directory
cd /d "%~dp0japi_cli"

echo Installing with pip...
echo Running: pip install -e .
echo.

pip install -e .
if %errorlevel% neq 0 (
    echo.
    echo Error: Installation failed
    echo Please check that pip is installed and try again
    pause
    exit /b 1
)

echo.
echo =========================================
echo   Installation Complete!
echo =========================================
echo.
echo Test the installation:
echo   japi_cli --help
echo.
echo Connect to an emulator:
echo   japi_cli -t localhost -p 8080 api ping
echo.
echo Interactive mode:
echo   japi_cli -t localhost -p 8080 -i
echo.
echo =========================================
pause
