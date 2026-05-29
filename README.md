# Hume Health — Remotion Video Project

A [Remotion](https://www.remotion.dev) project for producing Hume Health
(Hume Pod) marketing creatives in code. Scaffolded via `npx create-video@latest`
and customised with the brand's palette and messaging.

The reference advertorial/PDP pages this project draws from live alongside the
code as `*.html` files in the repo root.

## Commands

Install dependencies:

```bash
npm install
```

Start the Remotion Studio (interactive preview):

```bash
npm run dev
```

Render the video to `out/`:

```bash
npx remotion render HumePromo out/hume-promo.mp4
```

Upgrade Remotion:

```bash
npm run upgrade
```

## Structure

| File | Purpose |
| --- | --- |
| `src/index.ts` | Entry point — registers the root. |
| `src/Root.tsx` | Registers compositions shown in Studio. |
| `src/HumePromo.tsx` | The `HumePromo` composition (vertical 9:16 ad). |
| `src/theme.ts` | Brand colors and canonical render dimensions. |
| `remotion.config.ts` | Render configuration. |

## The `HumePromo` composition

A 1080×1920 (9:16), 8-second vertical ad built for social. All copy is exposed
as `defaultProps`, so you can edit the headline, subhead, metric, and CTA live
in Studio or override them per render:

```bash
npx remotion render HumePromo out/variant.mp4 \
  --props='{"headline":"Validated to within 1–2% of a $3,000 DEXA scan."}'
```
