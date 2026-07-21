import { app, BrowserWindow, globalShortcut, ipcMain } from 'electron';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

// Determine if we are in development mode
const isDev = !app.isPackaged;

function startBackend() {
  let pythonPath = 'python';
  const backendDir = path.join(__dirname, '..', '..', 'backend');

  if (isDev) {
    // Points to the python virtual environment executable
    pythonPath = path.join(backendDir, 'venv', 'Scripts', 'python');
    if (process.platform === 'win32') {
      pythonPath += '.exe';
    }

    console.log(`[Electron Main] Spawning development backend from: ${pythonPath}`);
    backendProcess = spawn(
      pythonPath,
      ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
      { cwd: backendDir }
    );
  } else {
    // Production binary packaged via PyInstaller
    const binaryName = process.platform === 'win32' ? 'atlas-backend.exe' : 'atlas-backend';
    const binaryPath = path.join(process.resourcesPath, 'bin', binaryName);

    console.log(`[Electron Main] Spawning production backend from: ${binaryPath}`);
    backendProcess = spawn(binaryPath, [], {
      cwd: path.dirname(binaryPath)
    });
  }

  backendProcess.stdout?.on('data', (data) => {
    console.log(`[FastAPI stdout]: ${data.toString().trim()}`);
  });

  backendProcess.stderr?.on('data', (data) => {
    console.error(`[FastAPI stderr]: ${data.toString().trim()}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`[FastAPI] Backend process exited with code ${code}`);
  });
}

function createWindow() {
  const distPath = path.join(__dirname, '..', '..', 'frontend', 'dist', 'index.html');

  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 500,
    show: false,
    frame: false,
    backgroundColor: '#09090b',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.once('ready-to-show', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });

  if (isDev) {
    let retries = 0;
    const loadDevServer = () => {
      mainWindow?.loadURL('http://localhost:5173').catch(() => {
        retries++;
        if (retries < 3) {
          console.log('[Electron Main] Retrying Vite dev server on http://localhost:5173...');
          setTimeout(loadDevServer, 1000);
        } else {
          console.log('[Electron Main] Vite server offline. Loading static built frontend...');
          mainWindow?.loadFile(distPath);
        }
      });
    };
    loadDevServer();
  } else {
    mainWindow.loadFile(distPath);
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Start backend FastAPI server
  startBackend();

  // Create UI Window
  createWindow();

  // Register Global Summon Hotkey (Alt + Space)
  const ret = globalShortcut.register('Alt+Space', () => {
    if (!mainWindow) return;
    if (mainWindow.isVisible() && mainWindow.isFocused()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
      mainWindow.focus();
      mainWindow.webContents.send('hotkey:summon');
    }
  });

  if (!ret) {
    console.error('[Electron Main] Global hotkey registration failed.');
  } else {
    console.log('[Electron Main] Global hotkey (Alt+Space) registered successfully.');
  }
});

// Window IPC handlers
ipcMain.on('window:minimize', () => {
  mainWindow?.minimize();
});

ipcMain.on('window:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});

ipcMain.on('window:close', () => {
  mainWindow?.hide(); // Hide instead of terminate to keep running 24/7 in background
});

// App termination cleanup
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  if (backendProcess) {
    console.log('[Electron Main] Terminating backend process...');
    backendProcess.kill();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
