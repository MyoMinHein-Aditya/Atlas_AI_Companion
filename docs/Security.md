# Security Guidelines & Threat Model — Atlas

Atlas has deep capabilities to execute shell commands and control OS processes. To protect the host operating system from malicious usage or accidental destruction, we enforce the following security framework.

---

## 1. Threat Model & Risk Vectors

1. **Destructive Shell Commands**: The LLM agent might accidentally generate or execute commands that delete files, format storage volumes, or terminate system processes.
2. **IPC Command Injection**: A compromise in the React renderer (e.g., via malicious third-party NPM libraries) attempts to send arbitrary terminal commands to Node's shell via the Electron IPC channels.
3. **API Key Theft**: Credential leakage through logs, crash reports, or committing configuration files to Github repositories.
4. **Browser Actions Compromise**: Automated browsers performing destructive operations or transactions in logged-in pages (e.g. cloud consoles, bank accounts).

---

## 2. Mitigation Strategies & Security Controls

### 2.1 IPC Sandboxing (Electron UI Boundary)
- **Node Integration**: Disabled (`nodeIntegration: false`) in all Renderers.
- **Context Isolation**: Enabled (`contextIsolation: true`) to isolate main process contexts from renderer scripts.
- **IPC Sanitation**: The preload bridge exposes only specific, typed functions with input sanitization. The renderer cannot execute raw system commands or import the `child_process` module.

### 2.2 Shell Execution Safety Gates
- **CLI Analyzer**: The FastAPI backend intercepts all planned commands before passing them to the shell runner.
- **Command Blacklist**: Any commands matching strings like `rm -rf`, `del /s`, `format`, `mkfs`, or administrative elevation triggers (`sudo`, `runas`) are immediately suspended.
- **Explicit Consent Dialog**: Atlas displays a prominent security UI card containing the exact script, the directories targeted, and a warning label. The execution is blocked until the user clicks **Approve**.

```text
+---------------------------------------+
|          SECURITY AUTHORIZATION       |
|                                       |
|  Atlas wants to run the following:    |
|  $ pip install -r requirements.txt    |
|                                       |
|  [ Cancel ]               [ Approve ] |
+---------------------------------------+
```

### 2.3 Browser Automation Security (Playwright)
- **Separate Browser Profile**: Playwright runs in an isolated, temporary browser context. It does not load the user's primary Chrome profile by default unless explicitly configured and consented to by the user.
- **Financial Triggers**: If the browser detects form actions matching payment endpoints (`checkout`, `stripe.com`, `paypal.com`, `purchase`), the automation stops immediately and hands control back to the user.

### 2.4 API Credential Security
- **Environments**: API keys (`GEMINI_API_KEY`, `GROQ_API_KEY`) are read strictly from local environmental memory.
- **Sanitized Logging**: The application loggers filter out authorization headers, token strings, and variables containing the suffix `_KEY` or `_PASSWORD`.
