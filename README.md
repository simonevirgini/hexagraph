# Hexagraph

Editor di disegno a **tessere esagonali**. Si compongono tessere geometriche
in bianco e nero sui sei lati di una griglia a nido d'ape — con livelli,
fusioni, colore, simmetrie, pattern, animazione ed export. Ispirato a
[glyphdrawing.club](https://glyphdrawing.club) (versione quadrata) e ai
Milimbo "Graphic Blocks".

> **A hexagonal-tile drawing tool.** Place black-and-white geometric tiles on a
> honeycomb grid, with layers, boolean-style merges, colour, symmetry, patterns,
> animation and export.

## Come si usa

È un **unico file HTML**, senza dipendenze né build. Bastano due strade:

- **Aprilo e basta:** doppio clic su `index.html` (si apre nel browser).
- **Online:** pubblica la cartella su un hosting statico qualsiasi.

Alla prima apertura parte un breve **tutorial**; la **barra in basso** dice
sempre cosa puoi fare. La guida si rigioca da **Info** (in fondo alla libreria).

## Cosa sa fare

- **Libreria di tessere** geometriche (pieni, tondi, cornici, linee, curve) +
  tessere **forgiate** da te.
- **Strumenti:** matita, gomma, secchiello, lazo a esagoni, selezione,
  **dither** A→B stile Aseprite, **contagocce**.
- **Fusioni** nella stessa cella: unisci ⊕, sottrai ⊖, interseca ∩, escludi ⊻.
- **Livelli** con blend risograph, **colore** per cella/livello.
- **Simmetrie** (specchi e rotazioni), **modalità pattern** (rettangolo,
  striscia, esagono, rombo) con anteprima ripetuta in tempo reale.
- **Timeline** di animazione (onion skin, loop ping-pong, export GIF/WEBM/PNG).
- **Export** PNG e SVG (con dimensioni in mm per la stampa).
- Salva/carica progetti in JSON.

## File del progetto

- `index.html` — tutta l'app (HTML + canvas + JS vanilla).
- `tiles.js` — i dati delle tessere base.
- `Ahamono.otf` — font dell'interfaccia.
- `HANDOFF.md` — note tecniche di sviluppo (architettura, modello dati).

## Licenza

Gratuito per uso **personale e commerciale**. Una **citazione è gradita**
(ma non obbligatoria). Dettagli in [LICENSE](LICENSE).

Fatto con cura da **Simone Virgini**. 🌸
