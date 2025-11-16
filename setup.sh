#!/bin/bash
# Setup script for Audio Transcription App

set -e

echo "==================================="
echo "Audio Transcription App - Setup"
echo "==================================="
echo ""

# Check for required dependencies
echo "Checking dependencies..."

# Check for git
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git first."
    exit 1
fi

# Check for make
if ! command -v make &> /dev/null; then
    echo "Error: make is not installed. Please install build-essential (Ubuntu/Debian) or equivalent."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3."
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed."
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Fedora: sudo dnf install ffmpeg"
    exit 1
fi

echo "All dependencies found!"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo "Python dependencies installed!"
echo ""

# Clone and build whisper.cpp
if [ ! -d "whisper.cpp" ]; then
    echo "Cloning whisper.cpp repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    echo "whisper.cpp cloned!"
else
    echo "whisper.cpp directory already exists, skipping clone."
fi

echo ""
echo "Building whisper.cpp..."
cd whisper.cpp

# Try to build with make directly first
# On macOS, we can compile without cmake
if make main 2>/dev/null; then
    echo "whisper.cpp built successfully with make!"
elif command -v cmake &> /dev/null; then
    echo "Building with cmake..."
    cmake -B build
    cmake --build build --config Release
    # Copy executable to main directory
    if [ -f "build/bin/main" ]; then
        cp build/bin/main ./main
    elif [ -f "build/bin/Release/main" ]; then
        cp build/bin/Release/main ./main
    fi
    echo "whisper.cpp built successfully with cmake!"
else
    echo ""
    echo "Note: cmake is not installed. Trying direct compilation..."
    echo "Compiling main executable..."
    # Compile directly for macOS ARM
    c++ -std=c++11 -O3 -I. -Iggml/include -Iggml/src \
        ggml/src/ggml.c ggml/src/ggml-alloc.c ggml/src/ggml-backend.c \
        ggml/src/ggml-quants.c ggml/src/ggml-aarch64.c \
        src/whisper.cpp examples/main/main.cpp \
        -o main \
        -framework Accelerate \
        || {
            echo ""
            echo "Error: Failed to compile whisper.cpp"
            echo "Please install cmake with: brew install cmake"
            echo "Then run this script again."
            cd ..
            exit 1
        }
    echo "whisper.cpp built successfully!"
fi

cd ..
echo ""

# Download Whisper model
mkdir -p models
if [ ! -f "models/ggml-base.bin" ]; then
    echo "Downloading Whisper base model (this may take a few minutes)..."
    bash whisper.cpp/models/download-ggml-model.sh base
    mv whisper.cpp/models/ggml-base.bin models/
    echo "Whisper model downloaded!"
else
    echo "Whisper model already exists, skipping download."
fi

echo ""
echo "==================================="
echo "Setup completed successfully!"
echo "==================================="
echo ""
echo "To start the application, run:"
echo "  python3 app.py"
echo ""
echo "Then open your browser at: http://localhost:8000"
echo ""
echo "Note: You can download different Whisper models (tiny, base, small, medium, large)"
echo "      by running: bash whisper.cpp/models/download-ggml-model.sh <model-name>"
echo "      and updating the model_path in app.py"
echo ""
