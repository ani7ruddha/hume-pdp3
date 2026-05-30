import type { HookIntroProps } from "./HookIntro";

const EYEBROW = "Hume · Body Intelligence";

// First-person UGC hook variants for the "Jack 16X9" testimonial.
// Each keeps the same format — only the opening hook changes. The `highlight`
// segment is rendered in Canela Text italic (brand cream).
export const hooks: { id: string; props: HookIntroProps }[] = [
  {
    id: "Hook-Recomp",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "Same bodyweight." },
        { text: "Completely different body.", highlight: true },
      ],
    },
  },
  {
    id: "Hook-Muscle",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "I lost 9 lbs of fat and gained" },
        { text: "6 lbs of muscle.", highlight: true },
      ],
    },
  },
  {
    id: "Hook-Scale",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "My scale was" },
        { text: "lying to me.", highlight: true },
        { text: "The data proved it." },
      ],
    },
  },
  {
    id: "Hook-Measure",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "I stopped weighing myself. I started measuring" },
        { text: "what actually matters.", highlight: true },
      ],
    },
  },
  {
    id: "Hook-Skinny",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "Skinny isn't the same as" },
        { text: "healthy.", highlight: true },
        { text: "I learned that the hard way." },
      ],
    },
  },
  {
    id: "Hook-Intelligence",
    props: {
      eyebrow: EYEBROW,
      segments: [
        { text: "I don't track weight anymore. I track my" },
        { text: "body intelligence.", highlight: true },
      ],
    },
  },
];
