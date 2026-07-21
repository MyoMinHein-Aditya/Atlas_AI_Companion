# Development Rules & Coding Standards — Atlas

This document outlines the engineering guidelines, styling standards, and architectural rules for all contributors and agent engines.

---

## 1. Core Engineering Principles

- **SOLID & DRY**: Write single-purpose classes/functions. Reuse utility utilities, avoiding duplicated logic.
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering. Do not write complex multi-layer abstractions unless a feature's scope specifically demands them.
- **Strict Typing**: All React/TypeScript code must have explicit types. Avoid using `any` unless absolutely necessary; document the reason why if used.
- **Asynchronous Flow**: Use async/await for all I/O operations (API calls, database queries, file writing).

---

## 2. Style Guide & Design Token Rules

All UI components must adhere to the 2035 glassmorphism aesthetic:
- **Color Palette**: Minimalistic dark mode. Neutral grays (`#0a0a0a` to `#262626`) paired with glowing accent highlights (e.g., cyan/purple gradients).
- **Glassmorphism Spec**:
  ```css
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  ```
- **Typography**: Primary font: `Geist Sans` or `Inter`. Monospace: `Geist Mono`.
- **Transitions**: Smooth easing curves (`cubic-bezier(0.16, 1, 0.3, 1)`) for all hover and active states.

---

## 3. Desktop Shell & IPC Conventions

- **Security First**: Never enable `nodeIntegration` in the React renderer.
- **Preload Sandboxing**: Expose only specific safe functions to the window using `contextBridge.exposeInMainWorld()`.
- **IPC Naming Format**:
  - `to-main:domain:action` (e.g., `to-main:window:minimize`)
  - `to-renderer:domain:event` (e.g., `to-renderer:notification:received`)
- Do not pass raw shell commands from Renderer to Main.

---

## 4. Backend Rules (Python & FastAPI)

- **Style Standard**: Conform to PEP 8 formatting rules.
- **Type Hints**: Mandatory for all function signatures and endpoints.
- **Validation**: Use Pydantic V2 models for validating request payloads and configuration inputs.
- **DB Session Management**: Always use dependency injection for SQLAlchemy sessions (`Depends(get_db)`) to ensure connections are closed.

---

## 5. AI Safety & Consent Thresholds

To prevent catastrophic events on the host OS, the backend automation engines must check against these bounds:
- **Safety Prompt Filters**: Intercept prompts that seek system file deletion (`rmdir`, `rm -rf`, `Format-Volume`).
- **Confirmation Guards**: Trigger an explicit UI pop-up and wait for approval before:
  - Deleting any user file.
  - Executing CLI commands with admin/sudo privileges.
  - Submitting forms in the web automation context containing payment/checkout keywords.
- **Secret Management**: Do not commit `.env` files or log API keys to system output files.
