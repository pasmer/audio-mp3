# 🎙️ Audio Transcription App

Applicazione web per trascrivere file audio (MP3, WAV, OGG, M4A) in testo usando **whisper-cpp** in locale.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

## ✨ Caratteristiche

- 📤 **Upload semplice**: Carica file audio tramite drag & drop o selezione file
- 🔒 **Privacy totale**: Tutti i file vengono processati localmente sul tuo server
- 🚀 **Whisper-cpp**: Utilizzo di whisper-cpp per trascrizioni veloci e accurate
- 💾 **Download immediato**: Scarica la trascrizione in formato TXT
- 🎨 **Interfaccia moderna**: UI responsive e user-friendly
- 📦 **Formati multipli**: Supporto per MP3, WAV, OGG, M4A

## 🛠️ Requisiti

### Sistema Operativo
- Linux / macOS / Windows

### Dipendenze
- **Python 3.8+**
- **ffmpeg** (per conversione audio)
- **git**
- **make** e compilatore C++ (per whisper.cpp)

### Installazione Dipendenze

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg git build-essential
```

#### macOS
```bash
brew install python ffmpeg git cmake
```

**Nota:** cmake è necessario per compilare whisper.cpp su macOS.

#### Fedora/RHEL
```bash
sudo dnf install python3 python3-pip ffmpeg git gcc-c++ make
```

#### Windows
1. Installa [Python](https://www.python.org/downloads/)
2. Installa [Git](https://git-scm.com/)
3. Installa [ffmpeg](https://ffmpeg.org/download.html)
4. Installa [CMake](https://cmake.org/download/)

## 🚀 Installazione

### Setup Automatico (Linux/macOS)

```bash
# Clona il repository
git clone <repository-url>
cd audio-mp3

# Esegui lo script di setup
./setup.sh
```

Lo script di setup:
- Installa le dipendenze Python
- Clona e compila whisper.cpp
- Scarica il modello Whisper base (~150MB)

### Setup Manuale

1. **Installa le dipendenze Python:**
```bash
pip3 install -r requirements.txt
```

2. **Clona e compila whisper.cpp:**
```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
cd ..
```

3. **Scarica il modello Whisper:**
```bash
mkdir -p models
bash whisper.cpp/models/download-ggml-model.sh base
mv whisper.cpp/models/ggml-base.bin models/
```

## 📖 Utilizzo

### Avviare l'applicazione

```bash
python3 app.py
```

L'applicazione sarà disponibile su: **http://localhost:5000**

### Usare l'applicazione

1. Apri il browser su `http://localhost:5000`
2. Carica un file audio (MP3, WAV, OGG, M4A)
3. Clicca su "Inizia Trascrizione"
4. Attendi il completamento (il tempo dipende dalla lunghezza dell'audio)
5. Scarica il file di testo con la trascrizione

## 🎯 Modelli Whisper

L'applicazione usa il modello **base** per default. Puoi usare altri modelli:

| Modello | Dimensione | Memoria | Velocità | Accuratezza |
|---------|------------|---------|----------|-------------|
| tiny    | 75 MB      | ~390 MB | Massima  | Bassa       |
| base    | 142 MB     | ~500 MB | Alta     | Media       |
| small   | 466 MB     | ~1 GB   | Media    | Buona       |
| medium  | 1.5 GB     | ~2.6 GB | Bassa    | Molto Buona |
| large   | 2.9 GB     | ~4.7 GB | Minima   | Massima     |

### Cambiare modello

1. **Scarica il modello:**
```bash
bash whisper.cpp/models/download-ggml-model.sh medium
mv whisper.cpp/models/ggml-medium.bin models/
```

2. **Modifica `app.py`:**
```python
# Cambia questa riga (circa linea 65):
model_path = './models/ggml-medium.bin'  # invece di ggml-base.bin
```

## 🏗️ Struttura del Progetto

```
audio-mp3/
├── app.py                 # Backend Flask
├── requirements.txt       # Dipendenze Python
├── setup.sh              # Script di setup (Linux/macOS)
├── setup.bat             # Script di setup (Windows)
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css     # Stili
│   └── js/
│       └── app.js        # Logica frontend
├── uploads/              # File temporanei (auto-creata)
├── transcriptions/       # Trascrizioni salvate (auto-creata)
├── whisper.cpp/          # Repository whisper.cpp (installato da setup)
└── models/               # Modelli Whisper (installati da setup)
```

## 🔧 Configurazione

### Variabili in `app.py`

```python
UPLOAD_FOLDER = 'uploads'              # Directory upload temporanei
TRANSCRIPTION_FOLDER = 'transcriptions' # Directory trascrizioni
MAX_FILE_SIZE = 500 * 1024 * 1024     # 500MB limite upload
```

### Porta e Host

Modifica l'ultima riga di `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia la porta qui
```

## 🐛 Risoluzione Problemi

### Errore: "whisper-cpp not installed"
Assicurati di aver compilato whisper.cpp:
```bash
cd whisper.cpp && make && cd ..
```

### Errore: "Whisper model not found"
Scarica il modello:
```bash
bash whisper.cpp/models/download-ggml-model.sh base
mv whisper.cpp/models/ggml-base.bin models/
```

### Errore: "ffmpeg not found"
Installa ffmpeg:
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Scarica da [ffmpeg.org](https://ffmpeg.org/download.html)

### Errore: "cmake: No such file" su macOS
Durante il setup, se vedi l'errore `cmake: No such file or directory`:

**Soluzione 1 (Consigliata):**
```bash
brew install cmake
./setup.sh
```

**Soluzione 2 (Manuale):**
```bash
cd whisper.cpp
make main
cd ..
mkdir -p models
bash whisper.cpp/models/download-ggml-model.sh base
mv whisper.cpp/models/ggml-base.bin models/
```

### L'upload è lento
- Verifica la dimensione del file (max 500MB)
- Per file grandi, usa un modello più piccolo (tiny o base)

### La trascrizione non è accurata
- Usa un modello più grande (medium o large)
- Verifica la qualità dell'audio originale
- Per lingue diverse dall'inglese, assicurati che il modello supporti quella lingua

## 🌐 Lingue Supportate

Whisper supporta oltre 90 lingue, tra cui:
- Italiano
- Inglese
- Spagnolo
- Francese
- Tedesco
- E molte altre...

## 📝 API Endpoints

### `POST /api/upload`
Upload e trascrizione file audio

**Request:** FormData con campo `file`

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "message": "Transcription completed successfully"
}
```

### `GET /api/download/<job_id>`
Download trascrizione

**Response:** File TXT

### `GET /api/status`
Verifica stato sistema

**Response:**
```json
{
  "whisper_installed": true,
  "model_available": true,
  "ffmpeg_available": true
}
```

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per i dettagli.

## 🙏 Ringraziamenti

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Port C/C++ di OpenAI Whisper
- [OpenAI Whisper](https://github.com/openai/whisper) - Modello originale
- [Flask](https://flask.palletsprojects.com/) - Framework web

## 🤝 Contributi

Contributi, issues e feature requests sono benvenuti!

## 📧 Supporto

Per problemi o domande, apri una issue su GitHub.

---

Realizzato con ❤️ usando whisper-cpp
