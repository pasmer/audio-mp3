// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const transcribeBtn = document.getElementById('transcribeBtn');
const cancelBtn = document.getElementById('cancelBtn');
const progressSection = document.getElementById('progressSection');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
const downloadBtn = document.getElementById('downloadBtn');
const newTranscriptionBtn = document.getElementById('newTranscriptionBtn');
const errorSection = document.getElementById('errorSection');
const errorText = document.getElementById('errorText');
const retryBtn = document.getElementById('retryBtn');
const statusSection = document.getElementById('statusSection');
const statusText = document.getElementById('statusText');

let selectedFile = null;
let currentJobId = null;

// Check system status on load
window.addEventListener('DOMContentLoaded', checkStatus);

async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        const indicator = statusSection.querySelector('.status-indicator');

        if (status.whisper_installed && status.model_available && status.ffmpeg_available) {
            indicator.classList.add('success');
            statusText.textContent = 'Sistema pronto per la trascrizione';
        } else {
            indicator.classList.add('warning');
            let missing = [];
            if (!status.whisper_installed) missing.push('whisper-cpp');
            if (!status.model_available) missing.push('modello whisper');
            if (!status.ffmpeg_available) missing.push('ffmpeg');
            statusText.textContent = `Attenzione: ${missing.join(', ')} non configurato. Consulta il README.`;
        }
    } catch (error) {
        const indicator = statusSection.querySelector('.status-indicator');
        indicator.classList.add('error');
        statusText.textContent = 'Impossibile verificare lo stato del sistema';
    }
}

// Upload area click
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File selection
fileInput.addEventListener('change', (e) => {
    handleFileSelection(e.target.files[0]);
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    handleFileSelection(file);
});

function handleFileSelection(file) {
    if (!file) return;

    const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/x-m4a'];
    const allowedExtensions = ['.mp3', '.wav', '.ogg', '.m4a'];

    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        showError('Formato file non valido. Usa MP3, WAV, OGG o M4A.');
        return;
    }

    if (file.size > 500 * 1024 * 1024) {
        showError('Il file è troppo grande. Dimensione massima: 500MB.');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Cancel button
cancelBtn.addEventListener('click', resetUpload);

function resetUpload() {
    selectedFile = null;
    currentJobId = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// Transcribe button
transcribeBtn.addEventListener('click', startTranscription);

async function startTranscription() {
    if (!selectedFile) return;

    // Hide file info, show progress
    fileInfo.style.display = 'none';
    progressSection.style.display = 'block';
    progressText.textContent = 'Caricamento del file...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        progressText.textContent = 'Trascrizione in corso... Questo potrebbe richiedere alcuni minuti.';

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Errore durante la trascrizione');
        }

        currentJobId = data.job_id;

        // Show success
        progressSection.style.display = 'none';
        resultSection.style.display = 'block';

    } catch (error) {
        progressSection.style.display = 'none';
        showError(error.message);
    }
}

// Download button
downloadBtn.addEventListener('click', () => {
    if (currentJobId) {
        window.location.href = `/api/download/${currentJobId}`;
    }
});

// New transcription button
newTranscriptionBtn.addEventListener('click', resetUpload);

// Retry button
retryBtn.addEventListener('click', () => {
    errorSection.style.display = 'none';
    fileInfo.style.display = 'block';
});

function showError(message) {
    errorText.textContent = message;
    errorSection.style.display = 'block';
    progressSection.style.display = 'none';
    fileInfo.style.display = 'none';
}
