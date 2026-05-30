import { continueRender, delayRender, staticFile } from "remotion";

// PRIMARY FONT — Red Hat Display (headlines + body). Self-hosted from
// public/fonts so renders don't depend on Google Fonts being reachable.
export const primaryFont = "Red Hat Display";

// SECONDARY FONT — Canela Text (highlights only). Canela is a licensed
// typeface (Commercial Type) and is NOT bundled. Drop the licensed file at
//   public/fonts/CanelaText-LightItalic.woff2
// and it is picked up automatically; until then we fall back to an elegant
// serif italic so renders never break.
export const highlightFont = '"Canela Text", "Canela", Georgia, "Times New Roman", serif';

let registered = false;
export const ensureFonts = () => {
  if (registered || typeof document === "undefined") return;
  registered = true;

  const handle = delayRender("Registering brand fonts");
  const style = document.createElement("style");
  style.textContent = `
    @font-face {
      font-family: "Red Hat Display";
      font-style: normal;
      font-weight: 400 900;
      font-display: block;
      src: url("${staticFile("fonts/RedHatDisplay-Variable.woff2")}") format("woff2");
    }
    @font-face {
      font-family: "Canela Text";
      font-style: italic;
      font-weight: 300;
      font-display: swap;
      src: url("${staticFile("fonts/CanelaText-LightItalic.woff2")}") format("woff2");
    }
  `;
  document.head.appendChild(style);

  // Wait for the bundled primary font before rendering; the optional Canela
  // file is allowed to fall back, so we don't block on it.
  if (typeof document.fonts?.load === "function") {
    Promise.all([
      document.fonts.load('700 100px "Red Hat Display"'),
      document.fonts.load('400 100px "Red Hat Display"'),
    ])
      .catch(() => undefined)
      .finally(() => continueRender(handle));
  } else {
    continueRender(handle);
  }
};
