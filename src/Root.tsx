import React from "react";
import { Composition } from "remotion";
import { HumePromo, humePromoDefaults } from "./HumePromo";
import { video } from "./theme";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HumePromo"
        component={HumePromo}
        durationInFrames={video.durationInFrames}
        fps={video.fps}
        width={video.width}
        height={video.height}
        defaultProps={humePromoDefaults}
      />
    </>
  );
};
