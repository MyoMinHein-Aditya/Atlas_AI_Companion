# Product Requirements Document (PRD) — Atlas

## 1. Executive Summary & Vision

Atlas is not a chatbot or another ChatGPT wrapper. Atlas is an intelligent desktop operating companion designed to run locally on the user's computer, 24/7. Inspired by JARVIS, Her, and modern development environments like Cursor, Atlas is built to understand context, maintain persistent long-term memory, automate workflows, interact with the operating system, run browser automations, and proactively assist the user.

The final user experience must feel like a premium, state-of-the-art software system from the year 2035—combining ambient design, glassmorphism, fluid animations, and highly responsive voice/text inputs.

---

## 2. Core Personas & Scenarios

### 2.1 Target Audience
- **Developers & Engineers**: Seeking an assistant that can execute system commands, write code, manage local environments, and automate repetitive tasks.
- **Power Users & Knowledge Workers**: Looking to automate browsers, extract screen details, manage calendars, and draft messages.
- **Privacy-Conscious Individuals**: Demanding strict control over local data, screen recordings, and personal documents.

### 2.2 Core Scenarios
- **OS Assistance**: "Hey Atlas, close all my Chrome tabs containing 'social media' and open my VS Code project."
- **Browser Automation**: "Hey Atlas, go to my GitHub issues page, find any bugs assigned to me, and summarize them in a table."
- **Coding & Execution**: "Hey Atlas, write a python script to resize all PNGs in this folder and execute it."

---

## 3. Scope of Core Features

### 3.1 Conversational Interface (Text & Voice)
- Dual-mode input: Text (type-to-command) and voice (speech-to-text, text-to-speech).
- Hands-free wake word activation ("Hey Atlas").
- Conversational streaming responses with low latency.

### 3.2 Operating System & Application Control
- Screen capturing and OCR (MSS, Tesseract/Gemini Vision).
- Keyboard/mouse emulation (PyAutoGUI, pynput) for operating legacy applications.
- File system management (create, read, search, safety-filtered delete).

### 3.3 Memory & Context Preservation
- Local relational storage (PostgreSQL) for user preferences, historical transcripts, and semantic memory tags.
- Context window consolidation: automatically summarizing past interactions to fit model contexts.
- Local vector/semantic embeddings mapping user files, system state, and historical conversations.

### 3.4 Multi-Agent Automation Engine
- Execution planners that break high-level goals into step-by-step terminal or browser actions.
- Sandboxed execution safety: asking confirmation for any destructive commands or financial actions.

---

## 4. Phase 1 Scope: Foundations & IPC

To ensure a robust structure, Phase 1 focuses exclusively on establishing the boilerplate, configuring directories, and establishing zero-latency communication channels between:
1. **Frontend (React/Vite/TS/Tailwind)**: Renders the glassmorphism UI.
2. **Desktop Shell (Electron)**: Direct OS hook, window manager, and node-based system access.
3. **Backend Service (FastAPI/Python)**: Houses heavy-duty OS libraries, AI APIs (Gemini/Groq), and Database adapters.

### Phase 1 Deliverables
- [x] Folder structures and environment scaffolding setup.
- [x] Multi-process communication bridge (IPC and HTTP/WebSocket).
- [x] Glassmorphic layout wrapper demonstrating React + Tailwind + Framer Motion.
- [x] Initial Docker Compose configuration for PostgreSQL.

---

## 5. Security & Safety Principles
- **No Silent Deletions**: Deleting files or folders must trigger an explicit confirmation dialog.
- **Command Gatekeeping**: Running any command line operations requires user approval.
- **API Key Privacy**: Keys (Gemini/Groq) must reside in local `.env` and never leak in telemetry.
