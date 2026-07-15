#!/usr/bin/env bash
# Build di Cloudflare Pages: pubblica SOLO i file dell'app in dist/.
# La dashboard esegue `bash build.sh` — la lista dei file vive QUI, in git:
# se cambia (file aggiunti/rimossi) basta un commit, niente da toccare nella dashboard.
set -euo pipefail
mkdir -p dist dist/packs
cp index.html tiles.js _headers dist/
cp packs/manifest.js packs/*.js dist/packs/   # pack di tessere generate (round 39, tools/gen_tiles.py)
