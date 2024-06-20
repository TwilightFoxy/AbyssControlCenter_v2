@echo off

REM Check if Python 3.9 is installed
python --version 2>nul | findstr /C:"Python 3.9" >nul
if %errorlevel% neq 0 (
    echo Python 3.9 is not installed.
    echo Downloading Python 3.9.13...
    REM Download Python 3.9.13
    curl -o python-3.9.13.exe https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe
    echo Installing Python 3.9.13...
    REM Install Python 3.9.13
    start /wait python-3.9.13.exe /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo Failed to install Python 3.9.13.
        exit /b %errorlevel%
    )
    echo Python 3.9.13 installed successfully.
) else (
    echo Python 3.9.13 is already installed.
)

REM Check if pip is installed
pip --version 2>nul | findstr /C:"pip" >nul
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo Failed to install pip.
        exit /b %errorlevel%
    )
    echo pip installed successfully.
) else (
    echo pip is already installed.
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements.
    exit /b %errorlevel%
)
echo Requirements installed successfully.

REM Run the program
echo Running the program...
python main.py
