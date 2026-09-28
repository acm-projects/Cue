import { app, BrowserWindow } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Electron's main process owns the native window and app lifecycle.
const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** Creates the desktop window and loads the appropriate renderer bundle. */
function createWindow() {
  const window = new BrowserWindow({
    width: 1100,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      // Preload runs before React and exposes a carefully limited API.
      preload: path.join(__dirname, "preload.js"),
      // Keep the renderer separate from Electron's privileged Node.js APIs.
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  const devServerUrl = process.env.VITE_DEV_SERVER_URL;

  if (devServerUrl) {
    void window.loadURL(devServerUrl);
    return;
  }

  // Production loads Vite's static build from the local filesystem.
  void window.loadFile(path.join(__dirname, "../../dist/index.html"));
}

app.whenReady().then(() => {
  createWindow();

  // On macOS, re-create a window when the dock icon is selected.
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// macOS applications stay open after their last window closes.
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
