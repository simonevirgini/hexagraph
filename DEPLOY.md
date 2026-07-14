# Deploy di Hexagraph su Cloudflare Pages

Il sito è statico e autoconsistente (nessun build framework, nessuna dipendenza di rete).
La build serve solo a **pubblicare i file dell'app** (`index.html`, `tiles.js`, `_headers`; il font Sono è inline nell'index)
lasciando fuori le note interne (HANDOFF, AUDIT), la `mobile.html` deprecata, `esempi/` e `.claude/`.

## Impostazioni del progetto Cloudflare Pages

Al collegamento del repo GitHub `simonevirgini/hexagraph`:

- **Production branch:** `main`
- **Framework preset:** None
- **Build command:**
  ```
  bash build.sh
  ```
  (la lista dei file pubblicati vive in `build.sh`, in git: se cambia basta un commit,
  niente da toccare nella dashboard)
- **Build output directory:** `dist`
- **Root directory:** `/` (default)

Nessuna variabile d'ambiente.

## Dominio custom

Dopo il primo deploy (l'app sarà su `hexagraph.pages.dev`):

1. Progetto Pages → **Custom domains** → **Set up a custom domain** → `hexagraph.app`.
2. Il dominio è registrato su Cloudflare, quindi i record DNS li aggiunge in automatico.
3. Il certificato HTTPS viene emesso da solo (pochi minuti). Il `.app` è HSTS-preload:
   funziona solo in HTTPS, ma Pages lo gestisce senza interventi.

## Aggiornare il sito

`git push` su `main` → Cloudflare ricostruisce e ripubblica da solo.

## Nota

`dist/` è generata dalla build e ignorata da git (vedi `.gitignore`): non va committata.
