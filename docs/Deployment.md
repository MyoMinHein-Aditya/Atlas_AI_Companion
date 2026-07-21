# Deployment & Distribution — Atlas

This document outlines the packaging pipelines and compiler configurations required to bundle Atlas into a single-file, production-ready desktop installer.

---

## 1. Production Bundle Pipeline

To deliver a single desktop executable to the user, we compile each segment of the stack and package them together:

```text
+-----------------------+      +-------------------------+
|  React Static Assets  | ---> |  Electron Main Process  |
|  (npm run build)      |      |  (TypeScript compiler)  |
+-----------------------+      +-------------------------+
                                            |
                                            v (Electron Builder)
+-----------------------+      +-------------------------+
|  Python Backend Exe   | ---> |     Final Installer     |
|  (PyInstaller bundle) |      |   (.exe / dmg bundle)   |
+-----------------------+      +-------------------------+
```

---

## 2. Compiling the Python Backend (PyInstaller)

To avoid requiring users to install Python and virtual environments, we compile the FastAPI backend into a standalone native executable.
- **Tool**: PyInstaller
- **Command**:
  ```bash
  cd backend
  venv/Scripts/pyinstaller --clean --onefile --name=atlas-backend --distpath=../desktop/resources/bin app/main.py
  ```
- **Included Assets**: PyInstaller wraps all dependencies (uvicorn, pydantic, sqlalchemy, etc.) inside the `atlas-backend` binary.

---

## 3. Configuring Electron Builder (desktop/package.json)

We configure Electron Builder to include the compiled Python backend as an `extraResource` inside the application structure.

```json
{
  "build": {
    "appId": "com.atlas.desktop",
    "productName": "Atlas",
    "directories": {
      "output": "dist"
    },
    "files": [
      "out/**/*",
      "resources/**/*"
    ],
    "extraResources": [
      {
        "from": "resources/bin/${platform}",
        "to": "bin",
        "filter": [
          "**/*"
        ]
      }
    ],
    "win": {
      "target": ["nsis"],
      "icon": "assets/icon.ico"
    }
  }
}
```

---

## 4. Database Provisioning in Production

In development, we run PostgreSQL via Docker Compose. For the packaged client distribution:
- The installer verifies if PostgreSQL is running locally on target defaults.
- Alternatively, Atlas can connect to a cloud-hosted PostgreSQL instance (specified during user onboarding/setup pages).
- System environment configurations inside the production client override local defaults to point to the production database host.
