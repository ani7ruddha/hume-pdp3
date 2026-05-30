import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { brand, gradients } from "./theme";
import { primaryFont, highlightFont, ensureFonts } from "./fonts";

// A hook is a sequence of text segments. `highlight: true` segments are
// rendered in Canela Text italic + the brand cream accent.
export type HookSegment = { text: string; highlight?: boolean };

export type HookIntroProps = {
  eyebrow: string;
  segments: HookSegment[];
};

// Flatten segments into individual words so they can be revealed one-by-one,
// keeping track of which words belong to a highlighted segment.
type Word = { text: string; highlight: boolean };
const toWords = (segments: HookSegment[]): Word[] =>
  segments.flatMap((seg) =>
    seg.text
      .trim()
      .split(/\s+/)
      .map((text) => ({ text, highlight: Boolean(seg.highlight) })),
  );

const WordSpan: React.FC<{ word: Word; index: number }> = ({ word, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = 14 + index * 3; // eyebrow first, then stagger words
  const progress = spring({
    frame: frame - start,
    fps,
    config: { damping: 200, mass: 0.6 },
  });
  const translateY = interpolate(progress, [0, 1], [28, 0]);

  return (
    <span
      style={{
        display: "inline-block",
        opacity: progress,
        transform: `translateY(${translateY}px)`,
        marginRight: "0.28em",
        ...(word.highlight
          ? {
              fontFamily: highlightFont,
              fontStyle: "italic",
              fontWeight: 300,
              color: brand.cream,
            }
          : {
              fontFamily: primaryFont,
              fontWeight: 700,
              color: brand.white,
            }),
      }}
    >
      {word.text}
    </span>
  );
};

export const HookIntro: React.FC<HookIntroProps> = ({ eyebrow, segments }) => {
  ensureFonts();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const words = toWords(segments);

  // Eyebrow reveal.
  const eyebrowProgress = spring({ frame, fps, config: { damping: 200 } });

  // Slow gradient/glow drift for a premium "UI as art" feel.
  const drift = interpolate(frame, [0, durationInFrames], [0, 6]);

  // Accent underline grows in after the words land.
  const underline = spring({
    frame: frame - (14 + words.length * 3 + 4),
    fps,
    config: { damping: 200 },
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(160deg, ${gradients.hookBackdrop[0]}, ${gradients.hookBackdrop[1]})`,
      }}
    >
      {/* Soft radial glow — gradients & glows per the visual guideline. */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(60% 50% at 50% ${40 + drift}%, ${brand.blueDeep}66, transparent 70%)`,
        }}
      />

      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: "0 200px",
          textAlign: "center",
        }}
      >
        {/* Eyebrow */}
        <div
          style={{
            fontFamily: primaryFont,
            fontWeight: 500,
            letterSpacing: 8,
            textTransform: "uppercase",
            fontSize: 30,
            color: brand.sky,
            opacity: eyebrowProgress,
            transform: `translateY(${interpolate(eyebrowProgress, [0, 1], [16, 0])}px)`,
            marginBottom: 44,
          }}
        >
          {eyebrow}
        </div>

        {/* Hook headline, revealed word-by-word */}
        <div
          style={{
            fontSize: 104,
            lineHeight: 1.08,
            maxWidth: 1500,
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
          }}
        >
          {words.map((word, i) => (
            <WordSpan key={i} word={word} index={i} />
          ))}
        </div>

        {/* Thin accent underline */}
        <div
          style={{
            marginTop: 54,
            height: 4,
            width: interpolate(underline, [0, 1], [0, 260]),
            background: brand.blue,
            borderRadius: 4,
            opacity: underline,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
