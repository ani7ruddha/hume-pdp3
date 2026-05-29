// Hume Health brand tokens, pulled from the Hume Pod product pages.
export const brand = {
  navy: "#132042",
  green: "#00b67a",
  blue: "#31ABE8",
  blueDeep: "#0a65e0",
  greenTint: "#e8f5e9",
  offWhite: "#fafafa",
  white: "#ffffff",
  orange: "#e65100",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
} as const;

// Canonical render dimensions for a vertical (9:16) social ad.
export const video = {
  fps: 30,
  width: 1080,
  height: 1920,
  durationInFrames: 30 * 8, // 8 seconds
} as const;
