#!/usr/bin/env python3
"""
Audio Transcription App using whisper-cpp
Allows uploading MP3 files and transcribing them to text
"""

import os
import subprocess
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import logging

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
TRANSCRIPTION_FOLDER = 'transcriptions'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRANSCRIPTION_FOLDER'] = TRANSCRIPTION_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTION_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_wav(input_path, output_path):
    """Convert audio file to WAV format using ffmpeg"""
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-ar', '16000',  # 16kHz sample rate (whisper requirement)
            '-ac', '1',       # mono
            '-c:a', 'pcm_s16le',  # 16-bit PCM
            '-y',  # overwrite output file
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Audio converted successfully: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting audio: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please install ffmpeg.")
        return False


def transcribe_audio(wav_path, output_txt_path, model_name='base'):
    """Transcribe audio using whisper-cpp"""
    try:
        # Path to whisper-cpp executable - try multiple locations
        whisper_exe_options = [
            './whisper.cpp/build/bin/whisper-cli',  # new cmake build location
            './whisper.cpp/build/bin/main',          # deprecated cmake build
            './whisper.cpp/main',                     # make build location
        ]

        whisper_exe = None
        for exe_path in whisper_exe_options:
            if os.path.exists(exe_path):
                whisper_exe = exe_path
                break

        # Construct model path based on model name
        model_path = f'./models/ggml-{model_name}.bin'

        # Check if whisper and model exist
        if not whisper_exe:
            logger.error(f"whisper-cpp executable not found. Tried: {whisper_exe_options}")
            return False, "whisper-cpp not installed"

        if not os.path.exists(model_path):
            logger.error(f"Model not found at {model_path}")
            return False, f"Whisper model '{model_name}' not found. Please download it first."

        # Run whisper-cpp with optimized parameters for long audio files
        # Reduced memory usage for better handling of long recordings
        cmd = [
            whisper_exe,
            '-m', model_path,
            '-f', wav_path,
            '-l', 'it',       # Italian language
            '-t', '8',        # Use 8 threads for faster processing
            '-mc', '-1',      # No limit on text context tokens
            '-ml', '0',       # No limit on segment length
            '-ac', '1500',    # Limit audio context to reduce memory (instead of 0=all)
            '-bs', '3',       # Reduce beam size from 5 to 3 (less memory)
            '-bo', '3',       # Reduce best-of from 5 to 3 (less memory)
            '-pp',            # Print progress
            '-otxt',          # output as text file
            '-of', output_txt_path.replace('.txt', '')  # whisper adds .txt automatically
        ]

        logger.info(f"Running whisper command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Transcription completed: {output_txt_path}")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Error during transcription: {e.stderr}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: mp3, wav, ogg, m4a'}), 400

        # Get selected model (default to 'base' if not provided)
        model_name = request.form.get('model', 'base')

        # Validate model name
        valid_models = ['tiny', 'base', 'small', 'medium', 'large']
        if model_name not in valid_models:
            return jsonify({'error': f'Invalid model. Choose from: {", ".join(valid_models)}'}), 400

        # Generate unique ID for this transcription
        job_id = str(uuid.uuid4())

        # Save uploaded file
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
        file.save(original_path)
        logger.info(f"File uploaded: {original_path}")

        # Convert to WAV if necessary
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}.wav")
        if not filename.endswith('.wav'):
            logger.info(f"Converting {filename} to WAV...")
            if not convert_to_wav(original_path, wav_path):
                return jsonify({'error': 'Failed to convert audio file'}), 500
        else:
            wav_path = original_path

        # Transcribe
        output_txt_path = os.path.join(app.config['TRANSCRIPTION_FOLDER'], f"{job_id}.txt")
        logger.info(f"Starting transcription for job {job_id} with model {model_name}...")

        success, error_msg = transcribe_audio(wav_path, output_txt_path, model_name)

        # Clean up temporary files
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
            if os.path.exists(wav_path) and wav_path != original_path:
                os.remove(wav_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")

        if not success:
            return jsonify({'error': error_msg or 'Transcription failed'}), 500

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Transcription completed successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/download/<job_id>', methods=['GET'])
def download_transcription(job_id):
    """Download transcription text file"""
    try:
        txt_path = os.path.join(app.config['TRANSCRIPTION_FOLDER'], f"{job_id}.txt")

        if not os.path.exists(txt_path):
            return jsonify({'error': 'Transcription not found'}), 404

        return send_file(
            txt_path,
            as_attachment=True,
            download_name=f"transcription_{job_id}.txt",
            mimetype='text/plain'
        )

    except Exception as e:
        logger.error(f"Error in download_transcription: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Check if whisper-cpp is properly installed"""
    # Check multiple possible locations for whisper executable
    whisper_exe_options = [
        './whisper.cpp/build/bin/whisper-cli',  # new cmake build location
        './whisper.cpp/build/bin/main',          # deprecated cmake build
        './whisper.cpp/main',                     # make build location
    ]
    whisper_installed = any(os.path.exists(exe) for exe in whisper_exe_options)

    model_path = './models/ggml-base.bin'

    return jsonify({
        'whisper_installed': whisper_installed,
        'model_available': os.path.exists(model_path),
        'ffmpeg_available': subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
