# Project Task List — Atlas

This is the living document tracking all micro-tasks across development phases.

---

## Phase 1: Core Boilerplate & IPC (Completed)

- [x] Repository Setup & Scaffolding
  - [x] git init in root
  - [x] Create root `.gitignore`
  - [x] Create root `.env.example`
  - [x] Create `docker-compose.yml` for PostgreSQL
  - [x] Generate 14 core documentation files (`docs/`)
- [x] Backend Initialization (FastAPI)
  - [x] Create `backend/venv` virtual environment
  - [x] Write `backend/requirements.txt`
  - [x] Write FastAPI base app in `backend/app/main.py`
  - [x] Configure `backend/app/config.py` using pydantic-settings
- [x] Frontend Setup (React + Vite + TS + Tailwind)
  - [x] Initialize Vite project in `frontend/`
  - [x] Configure Tailwind CSS and setup global styles
  - [x] Create UI skeleton (Command bar & response stream panel)
- [x] Electron Integration (Desktop)
  - [x] Initialize Electron NPM workspace in `desktop/`
  - [x] Create main process launcher in `desktop/src/main.ts`
  - [x] Establish IPC bridge (minimize, maximize, close window)
- [x] Testing & Integration Verification
  - [x] Launch all processes concurrently
  - [x] Test IPC ping/pong between Frontend and Electron Main
  - [x] Test WebSocket connectivity between Frontend and FastAPI Backend

---

## Phase 2: Conversational Interfaces & Voice (Completed)

- [x] Gemini API Integration
- [x] Groq API Integration
- [x] WebSockets Audio Streamer
- [x] Audio capture and transcription (STT)
- [x] Speech synthesis (TTS)
- [x] Local Wake-Word detection

---

## Phase 3: Relational Memory & Profile Store (Completed)

- [x] PostgreSQL connection setup & SQLAlchemy integration
- [x] Sessions and Preferences schema design
- [x] Context consolidation logic (transcripts summarizer)
- [x] Profile indexing script

---

## Phase 4: OS Automation & Local Execution Engine (Completed)

- [x] Playwright web automation integration
- [x] Screen capturing & OCR modules (mss, Tesseract)
- [x] OS keyboard & mouse simulator hooks (PyAutoGUI, pynput)
- [x] CLI Sandboxed shell exec engine with validation prompts

---

## Phase 5: Multi-Agent Orchestration & Distribution (Completed)

- [x] Multi-agent coordinator setup
- [x] Packaging backend with PyInstaller
- [x] Configuring Electron Builder packaging
- [x] Installer generator testing

---

## Phase 6: Real-Time System Access, Silent Subprocesses & Path Resolver (Completed)

- [x] Added `find_local_folder`, `open_folder_in_explorer`, and `list_running_applications` in `backend/app/services/system.py`
- [x] Added `creationflags=subprocess.CREATE_NO_WINDOW` in `backend/app/services/executor.py` for 100% silent subprocess execution
- [x] Configured real-time system context auto-injection into every prompt turn in `backend/app/main.py`
- [x] Enforced complete database session history loading on every turn for persistent context memory
- [x] Added `tests/test_system_access.py` unit test suite (19/19 tests passing)
- [x] Synchronized remote repository `https://github.com/MyoMinHein-Aditya/Atlas_AI_Companion.git`
