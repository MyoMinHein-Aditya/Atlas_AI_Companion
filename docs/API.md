# API Specifications — Atlas

This file specifies the endpoints, protocols, and message types for all communications between the UI, Desktop Shell, and Backend.

---

## 1. FastAPI REST API

The backend runs locally by default on `http://localhost:8000`. All payloads are JSON.

### 1.1 Health Check
- **Route**: `GET /health`
- **Response**:
  ```json
  {
    "status": "healthy",
    "version": "0.1.0",
    "services": {
      "database": "connected"
    }
  }
  ```

### 1.2 Get Sessions
- **Route**: `GET /api/sessions`
- **Response**: An array of active and archived sessions.
  ```json
  [
    {
      "id": "e96fbcfa-bf63-4f9e-ad32-2d1b82bb81fb",
      "title": "React Setup Help",
      "created_at": "2026-07-15T20:00:00Z",
      "updated_at": "2026-07-15T20:10:00Z"
    }
  ]
  ```

### 1.3 Get Session Messages
- **Route**: `GET /api/sessions/{session_id}/messages`
- **Response**: Historical logs for a specific chat.

---

## 2. WebSocket Real-Time Channel

Used for low-latency voice transmission, live text streaming, and execution logging.
- **URL**: `ws://localhost:8000/ws/stream`

### 2.1 Messages sent by Client (UI -> Backend)

#### Text Prompt message
```json
{
  "type": "text_prompt",
  "session_id": "e96fbcfa-bf63-4f9e-ad32-2d1b82bb81fb",
  "content": "Summarize this directory"
}
```

#### Audio Stream chunk
```json
{
  "type": "audio_chunk",
  "data": "SGVsbG8gV29ybGQ=..." -- Base64 encoded PCM audio data
}
```

### 2.2 Messages sent by Server (Backend -> UI)

#### Chat Token stream
```json
{
  "type": "chat_token",
  "token": "Hello"
}
```

#### Execution Update
```json
{
  "type": "execution_status",
  "step": 2,
  "status": "RUNNING",
  "description": "Opening Playwright browser to load GitHub"
}
```

---

## 3. Electron IPC Channels (Renderer <=> Main)

These actions are handled in `desktop/src/main.ts` and exposed to the React frontend through the preload context bridge.

### 3.1 Window Controls (Renderer -> Main)
- `ipcRenderer.send('window:minimize')` - Minimizes the Atlas UI panel.
- `ipcRenderer.send('window:maximize')` - Toggles full-screen/normal modes.
- `ipcRenderer.send('window:close')` - Hides or closes the active overlay.

### 3.2 Native Trigger events (Main -> Renderer)
- `ipcRenderer.on('hotkey:summon')` - Dispatched when the user presses `Alt + Space` to focus and display Atlas command input.
- `ipcRenderer.on('power:suspend')` - Dispatched if the host system goes to sleep, allowing Atlas to pause active tasks.
