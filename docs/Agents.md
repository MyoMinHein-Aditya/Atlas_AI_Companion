# Multi-Agent Orchestration — Atlas

Atlas achieves complex desktop automations through a cooperative multi-agent architecture. Agents are specialized, isolated LLM sub-tasks that communicate with the central coordinator to execute, evaluate, and self-correct actions.

---

## 1. Agent Roles & Profiles

We define five distinct agent profiles in our backend orchestration service:

```text
       +-----------------------+
       |   Planner Agent       | <--- User Prompt
       +-----------------------+
                   |
     +-------------+-------------+
     |             |             |
     v             v             v
+----------+  +----------+  +----------+
| Browser  |  | OS Auto  |  | Vision/  |
| Agent    |  | Agent    |  | OCR Agent|
+----------+  +----------+  +----------+
```

### 1.1 Planner Agent (The Coordinator)
- **Objective**: Deconstruct vague user intentions into a sequential plan of atomic actions.
- **Inputs**: User prompt + current system state (active window, active folder path, network status).
- **Output**: JSON action pipeline (e.g., `[{ "step": 1, "agent": "browser", "action": "search_github" }]`).
- **Self-Correction**: Evaluates execution feedback. If a step fails, it modifies subsequent actions.

### 1.2 Chat Agent (The Voice/Persona)
- **Objective**: Manage conversation, answer queries using memory, and deliver synthesized text/speech to the user.
- **Inputs**: Conversational history + context facts + current prompt.
- **Output**: Streaming text tokens + TTS commands.

### 1.3 Web Browser Agent
- **Objective**: Drive a browser window to inspect or retrieve web content.
- **Underlying Tools**: Playwright.
- **Key Capabilities**: Page navigation, DOM element clicking, form entry, text scraping, page screenshots.

### 1.4 OS Automation Agent
- **Objective**: Interact with native desktop applications.
- **Underlying Tools**: PyAutoGUI, pynput, and shell command runners.
- **Key Capabilities**: Native window activation, mouse movement and clicking, keystroke input emulation, CLI script execution.

### 1.5 Vision & OCR Agent
- **Objective**: Interpret visual elements on the screen.
- **Underlying Tools**: `mss` (screenshot library) + Gemini Multi-modal / OCR API.
- **Key Capabilities**: Bounding box determination for buttons, reading text from images, locating graphical assets on the screen.

---

## 2. Agent Communication Schema

All agents write telemetry to the FastAPI logs and exchange data using a structured event schema:

```json
{
  "event_id": "evt_987654321",
  "source_agent": "planner",
  "target_agent": "browser",
  "command": "NAVIGATE_TO",
  "parameters": {
    "url": "https://github.com/issues"
  },
  "state_context": {
    "previous_step_status": "SUCCESS"
  }
}
```

---

## 3. Execution Safety Checkpoints

Before the **OS Automation Agent** or **Browser Agent** runs a step marked as "sensitive" (e.g. system shell executions), it must suspend execution and trigger a message to the Frontend asking for explicit user approval.
- **Approved**: Execution resumes.
- **Rejected**: The coordinator agent is notified of user cancellation and must re-plan or exit.
