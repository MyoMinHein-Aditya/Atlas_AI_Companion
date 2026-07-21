# Project Phases — Atlas Roadmap

Atlas will be built in five distinct development phases. Each phase represents a functional milestone that is fully compilable, testable, and documented.

---

## Phase 1: Core Boilerplate & Inter-Process Communication (Current)

Establish the structural foundation, build system setups, and communication lanes across the frontend, desktop shell, and local backend.
- **Goals**:
  - Scaffolding of React (Vite/TS), Electron (TS), and FastAPI (Python venv).
  - Setup of PostgreSQL container in Docker.
  - Implement basic HTTP endpoints and WebSockets in FastAPI.
  - Electron IPC setup to bridge Frontend components to Node's window events.
  - Single dev command to boot all three parts together.

---

## Phase 2: Conversational Interfaces & Voice

Add intelligence to Atlas by implementing the text-to-text, speech-to-text, and text-to-speech processing loops using Gemini and Groq.
- **Goals**:
  - Integrate Gemini Generative AI SDK and Groq API calls.
  - Implement a WebSocket pipeline for streaming audio recording.
  - Implement a Text-to-Speech (TTS) module and real-time Speech-to-Text (STT) parsing.
  - Introduce wake-word detection ("Hey Atlas") to summon the assistant.

---

## Phase 3: Relational Memory & Profile Store

Enable Atlas to remember prior sessions, learn user preferences, and load external files.
- **Goals**:
  - Establish PostgreSQL tables for users, chat sessions, settings, and memory nodes.
  - Implement a memory engine that automatically summarizes chat transcripts when context limits are reached.
  - Build metadata indexing for local user folders and profiles.

---

## Phase 4: OS Automation & Local Execution Engine

Empower Atlas to interact directly with the computer, automation-level libraries, and command lines.
- **Goals**:
  - Integrate Playwright to automate headless and headful web browsing tasks.
  - Integrate PyAutoGUI, pynput, and mss to take screenshots, read canvas pixels, perform mouse clicks, and type text.
  - Implement a secure Python-based local shell executor with safety gates (confirming destructive scripts before running).

---

## Phase 5: Multi-Agent Orchestration & Distribution

Coordinate multiple specialized agents and package the application into a distribution-ready desktop bundle.
- **Goals**:
  - Implement Planner-Executor design (Planner agent breaks down goals, Executor agent executes tasks, OCR/Vision agent watches screens).
  - Package the React static build inside the Electron client.
  - Package the Python FastAPI backend into a standalone binary using PyInstaller.
  - Configure Electron Builder to generate cross-platform installers (e.g., `.exe` for Windows).
