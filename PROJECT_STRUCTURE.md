# GlassBox - Final Project Structure

## ✅ Core Files (Keep)
```
IMPAD/
├── README.md ⭐
├── requirements.txt ⭐
├── .env (private)
├── .env.example ⭐
├── .gitignore
│
├── main_role.py          # Main orchestrator
├── dashboard_app (1).py  # Streamlit UI
├── SessionLogger.py      # Data logger
├── sensor.py             # Activity monitor
├── audio_listener.py     # Audio capture
│
├── cognitive_engine/     # AI analysis
│   ├── clarity_analyzer.py
│   ├── fake_llm.py
│   ├── system_prompt.py
│   └── llm_config.py
│
├── src/                  # New structure (partially migrated)
│   ├── core/
│   ├── sensors/
│   ├── cognitive/
│   └── dashboard/
│
├── data/                 # Session data
│   ├── transcripts/
│   └── (session_log.json)
│
├── docs/ ⭐
│   └── ARCHITECTURE.md
│
├── submissions/          # Submitted code
│
└── archive/              # Old/temp files (can delete)
    ├── cognitive_engine/ (old copy)
    ├── check_audio_devices.py
    └── temp_chunk.wav
```

## 🗑️ Files to Delete (Optional)
- `archive/` folder (after verifying nothing important)
- `src/` folder (incomplete migration)
- `cleanup.ps1` (after running once)
- Any `.wav` files in root
- `STOP_SESSION` file

## 📝 Active Files During Session
- `session_log.json` - Current session data
- `session_audio.wav` - Recorded audio
- `STOP_SESSION` - Signal file (auto-created/deleted)
- `temp_chunk.wav` - Temporary audio chunk

## 🎯 For Hackathon Presentation
**Include:**
- ✅ README.md
- ✅ docs/ARCHITECTURE.md
- ✅ requirements.txt
- ✅ .env.example
- ✅ All core `.py` files
- ✅ Sample `session_log.json`

**Exclude:**
- ❌ `.env` (contains API key!)
- ❌ `archive/` folder
- ❌ `__pycache__/`
- ❌ `.wav` files
