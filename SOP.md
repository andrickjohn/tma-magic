# TMA Magic Black Box — Standard Operating Procedure

## Quick Start

### 1. Install Dependencies
```bash
cd "TMA Project"
pip install -r requirements.txt
```

> **Note:** For PDF to image conversion, you also need `poppler`:
> - macOS: `brew install poppler`
> - Windows: Download from [poppler releases](https://github.com/osber/poppler/releases) and add to PATH

### 2. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Configuration

Settings are stored in:
- **macOS:** `~/.tma_magic/config.json`
- **Windows:** `%APPDATA%\TMA Magic\config.json`

### API Key Setup
1. Open the app
2. Click ⚙️ Settings
3. Enter your OpenAI API key
4. Key is saved automatically

---

## Extraction Modes

| Mode | Description | Cost |
|------|-------------|------|
| **Regex Only** | Pattern matching, instant results | Free |
| **AI Only** | GPT-4o Vision for all pages | ~$0.01/page |
| **Hybrid** | Regex first, AI if confidence < 85% | Variable |

---

## Testing

### Test Backend Directly
```bash
python backend_processor.py --test "Sample Data/2024 YE BS and PnL.pdf" --mode regex_only
```

### Expected Output Fields
- Revenue, Net Income, Depreciation (Income Statement)
- Assets, Liabilities (Balance Sheet)
- Total CPLTD (Cash Flow/Debt)

---

## Building Windows Executable

### Prerequisites
1. Windows machine (or VM)
2. Python 3.10+ installed
3. All dependencies: `pip install -r requirements.txt`

### Build Steps
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller build_windows.spec

# Output will be in dist/TMA Magic Black Box/
```

### Installer Creation
For a proper Windows installer, use [NSIS](https://nsis.sourceforge.io/) or [Inno Setup](https://jrsoftware.org/isinfo.php) to package the `dist/` folder.

---

## Troubleshooting

### "poppler not found"
Install poppler for PDF-to-image conversion:
```bash
# macOS
brew install poppler

# Windows
# Download and add to PATH
```

### UI Freezes
This should not happen with the subprocess architecture. If it does:
1. Check if `backend_processor.py` is running
2. Check temp files in system temp directory: `tma_status_*.json`

### Low Extraction Accuracy
1. Try AI mode for scanned documents
2. Check if PDF has selectable text (Regex needs this)
3. Reduce confidence threshold in settings

---

## File Structure
```
TMA Project/
├── app.py                 # Streamlit UI
├── backend_processor.py   # Extraction worker
├── config.py              # Settings management
├── engines/
│   ├── regex_engine.py    # Pattern-based extraction
│   └── ai_engine.py       # GPT-4o Vision extraction
├── utils/
│   └── pdf_parser.py      # PDF/Excel parsing
├── requirements.txt       # Dependencies
├── build_windows.spec     # PyInstaller config
└── SOP.md                 # This file
```
