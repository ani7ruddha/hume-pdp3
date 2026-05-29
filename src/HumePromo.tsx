import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { brand } from "./theme";

export type HumePromoProps = {
  headline: string;
  subhead: string;
  metric: string;
  metricLabel: string;
  cta: string;
};

export const humePromoDefaults: HumePromoProps = {
  headline: "Your scale is lying to you.",
  subhead: "Hume Pod reads 45+ body-composition metrics — in plain English.",
  metric: "45+",
  metricLabel: "metrics, every weigh-in",
  cta: "Stop guessing. Start progressing.",
};

// Reveals its children with a fade + upward slide, starting at `delay` frames.
const FadeUp: React.FC<{
  delay: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ delay, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200 },
  });
  const translateY = interpolate(progress, [0, 1], [40, 0]);
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${translateY}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const HumePromo: React.FC<HumePromoProps> = ({
  headline,
  subhead,
  metric,
  metricLabel,
  cta,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Subtle background drift for a premium feel.
  const drift = interpolate(frame, [0, durationInFrames], [0, 8]);

  // CTA pulse once it has appeared.
  const ctaPulse = 1 + 0.04 * Math.sin((frame / fps) * Math.PI * 2);

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% ${30 + drift}%, ${brand.blueDeep}22, ${brand.navy})`,
        fontFamily: brand.fontFamily,
        color: brand.white,
        padding: 100,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <FadeUp delay={4}>
        <div
          style={{
            fontSize: 34,
            letterSpacing: 6,
            textTransform: "uppercase",
            color: brand.green,
            fontWeight: 700,
          }}
        >
          Hume&nbsp;Health
        </div>
      </FadeUp>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 40,
        }}
      >
        <FadeUp delay={12}>
          <div style={{ fontSize: 92, fontWeight: 800, lineHeight: 1.05 }}>
            {headline}
          </div>
        </FadeUp>

        <FadeUp delay={34}>
          <div
            style={{
              fontSize: 44,
              fontWeight: 400,
              lineHeight: 1.3,
              color: "#cdd6ec",
            }}
          >
            {subhead}
          </div>
        </FadeUp>

        <FadeUp delay={56}>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 24,
              marginTop: 20,
              padding: "32px 44px",
              borderRadius: 28,
              background: brand.green,
              color: brand.navy,
              width: "fit-content",
              boxShadow: `0 20px 60px ${brand.green}44`,
            }}
          >
            <span style={{ fontSize: 120, fontWeight: 900 }}>{metric}</span>
            <span style={{ fontSize: 40, fontWeight: 600 }}>{metricLabel}</span>
          </div>
        </FadeUp>
      </div>

      <FadeUp delay={90}>
        <div
          style={{
            fontSize: 50,
            fontWeight: 700,
            textAlign: "center",
            transform: `scale(${ctaPulse})`,
            color: brand.blue,
          }}
        >
          {cta}
        </div>
      </FadeUp>
    </AbsoluteFill>
  );
};
