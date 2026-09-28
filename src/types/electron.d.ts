/** Types for the minimal API exposed by Electron's preload script. */
interface Window {
  // This property exists only because preload.ts exposes it securely.
  cue: {
    platform: NodeJS.Platform;
  };
}
