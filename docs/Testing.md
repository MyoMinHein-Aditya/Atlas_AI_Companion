# Testing Strategy & QA Plan — Atlas

This document describes the test environment configurations, validation scripts, and E2E frameworks utilized in Atlas.

---

## 1. Test Architecture

We split testing into three distinct layers to reflect the modular nature of the application components:

```text
+-----------------------+-------------------------+
| Layer                 | Framework / Tools       |
+-----------------------+-------------------------+
| Backend Unit tests    | pytest, httpx           |
| Frontend Components   | Vitest, Testing Library |
| Desktop E2E flows     | Playwright Electron     |
+-----------------------+-------------------------+
```

---

## 2. Backend Unit Testing (Python)

- **Library**: `pytest`
- **Location**: `tests/backend/`
- **Key Focus**:
  - Validating local command parser safety checks.
  - Database schema models mapping constraints.
  - Mocking Gemini and Groq API payloads.
- **Run command**:
  ```bash
  cd backend
  venv/Scripts/python -m pytest tests/
  ```

### Mocking LLM Integrations Example
We mock API responses from Google Generative AI to avoid external network dependencies and token costs during local testing:
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_assistant_chat_mock():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        mock_instance.generate_content_async = AsyncMock(
            return_value=AsyncMock(text="Mocked response from Gemini")
        )
        # Call backend Chat handler and assert
```

---

## 3. Frontend Unit & Component Testing (React)

- **Library**: `Vitest` + `@testing-library/react`
- **Location**: `tests/frontend/`
- **Key Focus**:
  - Renders of glassmorphic containers.
  - Input form actions and field validations.
  - Verification of simulated IPC triggers.
- **Run command**:
  ```bash
  cd frontend
  npm run test
  ```

---

## 4. End-to-End Testing (Electron + Playwright)

Playwright includes native integrations to spawn and automate Electron-based shells.
- **Location**: `tests/e2e/`
- **Key Focus**:
  - Verifying the application boots and loads the main window wrapper.
  - Dispatching native keyboard strokes (`Alt + Space`) and validating if the command overlay is focused.
  - Simulating Backend failure states and verifying the UI renders connection error panels.
- **Run command**:
  ```bash
  cd desktop
  npx playwright test
  ```
