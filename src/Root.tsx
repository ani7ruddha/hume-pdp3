import React from "react";
import { Composition } from "remotion";
import { HumePromo, humePromoDefaults } from "./HumePromo";
import { HookIntro } from "./HookIntro";
import { hooks } from "./hooks";
import { video, hook } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Vertical product ad */}
      <Composition
        id="HumePromo"
        component={HumePromo}
        durationInFrames={video.durationInFrames}
        fps={video.fps}
        width={video.width}
        height={video.height}
        defaultProps={humePromoDefaults}
      />

      {/* Hook intros (16:9) — one composition per variant, same format */}
      {hooks.map(({ id, props }) => (
        <Composition
          key={id}
          id={id}
          component={HookIntro}
          durationInFrames={hook.durationInFrames}
          fps={hook.fps}
          width={hook.width}
          height={hook.height}
          defaultProps={props}
        />
      ))}
    </>
  );
};
