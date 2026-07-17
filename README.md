# Hexagraph <sup>beta</sup>

**A free hexagonal-tile drawing editor.** Place geometric tiles on a honeycomb
grid and compose them into marks, patterns and animations — with layers,
boolean-style merges, colour, symmetry and print-ready export.

**Try it now → [hexagraph.app](https://hexagraph.app)** (runs in any desktop
browser, nothing to install).

![Hexagraph](og.png?v=2)

Inspired by [glyphdrawing.club](https://glyphdrawing.club) (the square-grid
original) and by Milimbo's "Graphic Blocks".

> Hexagraph is in **beta**: it works, it's used daily, and it still changes
> often. If something breaks, opening an issue helps a lot.

## What it does

- **Tile library** — 149 base geometric tiles (solids, rounds, frames, lines,
  curves), plus tiles you **forge** in the app and tiles you **import from
  SVG** (a template is provided; draw in Illustrator/Inkscape, import back).
- **Tools** — pencil (with an Aseprite-style *pixel-perfect* mode), eraser,
  bucket (contiguous or global), hex lasso, selection, **A→B dither
  gradients**, eyedropper.
- **Merges within one cell** — union ⊕, subtract ⊖, intersect ∩, exclude ⊻,
  applied in chronological order.
- **Layers** — blend modes (risograph-style multiply and friends), opacity,
  multi-select, merge/flatten with baked colours.
- **Symmetry** — mirrors and 2/3/6-fold rotations, drawn live.
- **Pattern mode** — rectangle, strip, hexagon or rhombus unit, repeated live
  on screen while you draw; exports the repetition as PNG or tiled SVG.
- **Animation timeline** — frames with onion skin, ping-pong loop, GIF / WEBM /
  PNG-sequence export.
- **Export** — PNG, JPG, SVG (with physical mm size, ready for print or plotter).
- Projects save/load as a single JSON file. UI in **English and Italian**.

## Run it

It's a **single HTML file** with no dependencies and no build step:

- **Online:** [hexagraph.app](https://hexagraph.app)
- **Locally:** clone the repo (or download it) and double-click `index.html`.

A short tutorial starts on first launch; the bar at the bottom always tells
you what you can do. Replay the guide from **Info** at the end of the library.

## Project files

- `index.html` — the whole app (HTML + canvas + vanilla JS).
- `tiles.js` — the base tile data.
- `tools/gen_tiles.py` + `packs/` — a systematic tile generator (3,728 extra
  canonical tiles in packs, currently not loaded by the app).
- UI font = **Sono** by Tyler Finck (SIL OFL), inlined as a data URI;
  licence in `Sono-OFL.txt`.

## Support

Hexagraph is free for **personal and commercial** use. If you enjoy it, a
credit and a link are appreciated — and you can support development via the
Sponsor button on this repo.

## License

[MIT](LICENSE) © 2026 Simone Virgini.

---

*In italiano:* Hexagraph è un editor di disegno a **tessere esagonali** —
livelli, fusioni, simmetrie, pattern, animazione ed export per la stampa.
Gratuito per uso personale e commerciale (licenza MIT), una citazione è
gradita. Si usa su [hexagraph.app](https://hexagraph.app) o aprendo
`index.html` in un browser desktop.
