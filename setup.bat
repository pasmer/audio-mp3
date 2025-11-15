@echo off
REM Setup script for Audio Transcription App (Windows)

echo ===================================
echo Audio Transcription App - Setup
echo ===================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/
    pause
    exit /b 1
)

REM Check for git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo All dependencies found!
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed!
echo.

REM Clone and build whisper.cpp
if not exist "whisper.cpp" (
    echo Cloning whisper.cpp repository...
    git clone https://github.com/ggerganov/whisper.cpp.git
    echo whisper.cpp cloned!
) else (
    echo whisper.cpp directory already exists, skipping clone.
)

echo.
echo Building whisper.cpp...
echo NOTE: You need to build whisper.cpp manually on Windows.
echo Please follow these steps:
echo   1. Install CMake from https://cmake.org/download/
echo   2. Open a command prompt in the whisper.cpp directory
echo   3. Run: mkdir build ^&^& cd build
echo   4. Run: cmake ..
echo   5. Run: cmake --build . --config Release
echo   6. Copy the main.exe from build/bin/Release/ to whisper.cpp/
echo.

REM Create models directory
if not exist "models" mkdir models

REM Download Whisper model
if not exist "models\ggml-base.bin" (
    echo Downloading Whisper base model...
    echo Please download the model manually from:
    echo https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
    echo And save it to: models\ggml-base.bin
    echo.
) else (
    echo Whisper model already exists.
)

echo.
echo NOTE: On Windows, you also need to install ffmpeg:
echo   1. Download from https://ffmpeg.org/download.html
echo   2. Extract and add to PATH
echo.

echo ===================================
echo Setup instructions provided!
echo ===================================
echo.
echo To start the application, run:
echo   python app.py
echo.
echo Then open your browser at: http://localhost:5000
echo.
pause
