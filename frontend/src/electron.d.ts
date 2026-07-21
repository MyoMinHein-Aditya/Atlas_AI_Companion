export interface ElectronAPI {
  minimize: () => void;
  maximize: () => void;
  close: () => void;
  onSummon?: (callback: () => void) => () => void;
}

declare global {
  interface Window {
    electron?: ElectronAPI;
  }
}
