# Fonts

## Canela Text (licensed — not bundled)

The brand's **secondary / highlight** font is **Canela Text** (Commercial Type),
a licensed typeface that cannot be redistributed in this repo.

To use it in renders, drop the licensed web font file here:

```
public/fonts/CanelaText-LightItalic.woff2
```

`src/fonts.ts` references that exact path. Until the file is present, highlighted
words fall back to a system serif italic (Georgia) so renders never break — the
layout and timing are identical.

The **primary** font, **Red Hat Display**, is loaded automatically from Google
Fonts via `@remotion/google-fonts` and needs no manual setup.
