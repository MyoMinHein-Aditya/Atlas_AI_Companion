import { contextBridge, ipcRenderer } from 'electron';

// Expose secure window APIs to the React renderer
contextBridge.exposeInMainWorld('electron', {
  minimize: () => ipcRenderer.send('window:minimize'),
  maximize: () => ipcRenderer.send('window:maximize'),
  close: () => ipcRenderer.send('window:close'),
  onSummon: (callback: () => void) => {
    const subscription = () => callback();
    ipcRenderer.on('hotkey:summon', subscription);
    return () => {
      ipcRenderer.removeListener('hotkey:summon', subscription);
    };
  }
});
