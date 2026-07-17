#!/usr/bin/env bash
# Build di Cloudflare Pages: pubblica SOLO i file dell'app in dist/.
# La dashboard esegue `bash build.sh` — la lista dei file vive QUI, in git:
# se cambia (file aggiunti/rimossi) basta un commit, niente da toccare nella dashboard.
set -euo pipefail
mkdir -p dist
cp index.html tiles.js _headers og.png dist/
# NB: packs/ NON si pubblica — i pack generati (tools/gen_tiles.py) vivono nel repo
# ma sono staccati dall'app dal round 42 (decisione di Simone). Vedi HANDOFF §6.
