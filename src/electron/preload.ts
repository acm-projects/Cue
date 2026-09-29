import { contextBridge } from "electron";

// Expose only deliberate, safe values to the renderer process.
// Add new desktop capabilities here instead of importing Electron in React.
contextBridge.exposeInMainWorld("cue", {
  platform: process.platform,
});
