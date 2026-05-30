// Hume Health brand tokens — sourced from the Creative Guideline (Figma).
// https://www.figma.com/design/hOwhzJz9XXfejZH9Fo1y2H/Creative-Guideline
export const brand = {
  // Primary
  blue: "#1a82ff", // electric blue
  sky: "#32aae7", // sky blue
  navy: "#132042", // deep navy
  ink: "#191717", // near-black
  white: "#f7f7f7", // off-white
  // Secondary
  slate: "#869cb7",
  blueMid: "#5f97c9",
  blueDeep: "#265289",
  cream: "#e6e4bd", // pale cream/gold — used for elegant highlights
  gray: "#dadadb",
  // Common text tone from the guideline
  textNavy: "#29364c",
} as const;

// Sophisticated gradients from the guideline ("high-def quality").
export const gradients = {
  deepBlue: ["#234a80", "#7e9bbb"] as const,
  blueGlow: ["#337bb5", "#b9d3e2"] as const,
  // Premium dark backdrop for hook cards (navy → near-black).
  hookBackdrop: ["#1b2c54", "#0a1124"] as const,
} as const;

// Vertical (9:16) product ad — the original HumePromo.
export const video = {
  fps: 30,
  width: 1080,
  height: 1920,
  durationInFrames: 30 * 8,
} as const;

// 16:9 hook intro — matches the "Jack 16X9" reference video.
export const hook = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInFrames: 30 * 3, // 3-second hook
} as const;
