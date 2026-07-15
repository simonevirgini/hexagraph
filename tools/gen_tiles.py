#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tiles.py — generatore sistematico di tessere per Hexagraph (round 39).

Idea: una tessera non è un disegno ma una SCELTA COMBINATORIA su un alfabeto
finito di 13 ancore (6 vertici V0..V5, 6 metà-lato M0..M5, centro C) di un
esagono flat-top di raggio 1. Ogni famiglia enumera TUTTE le scelte possibili,
poi si tiene un solo rappresentante per orbita del gruppo diedrale D6
(l'app fornisce già rot ×6 e flip = 12 varianti gratis per tessera).

Famiglie (→ un pack .js ciascuna in packs/):
  settori  — maschere di 12 mezzi-spicchi (riempimenti)
  corde    — 1..3 segmenti tra ancore (tratti)
  archi    — 1..3 archi di cerchio a centri/raggi quantizzati (tratti)
  anelli   — bande concentriche (cerchi e esagoni) a raggi quantizzati

Le 149 tessere esistenti in tiles.js vengono DECODIFICATE nello stesso
linguaggio di descrittori e escluse (niente doppioni con la libreria base).

Uso:  python3 tools/gen_tiles.py            # censimento + genera packs/
      python3 tools/gen_tiles.py --census   # solo censimento, non scrive
"""
import json, math, os, re, sys, hashlib, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COS, SIN, PI = math.cos, math.sin, math.pi

# ---------------------------------------------------------------- ancore ----
def vco(i): a = PI/3*i;        return (COS(a), SIN(a))          # vertice
def mco(i): a = PI/3*i + PI/6; return (0.8660254037844386*COS(a), 0.8660254037844386*SIN(a))  # metà-lato (raggio = apotema)
ANCHORS = {f'V{i}': vco(i) for i in range(6)}
ANCHORS.update({f'M{i}': mco(i) for i in range(6)})
ANCHORS['C'] = (0.0, 0.0)
APO = 0.8660254037844386                       # apotema = √3/2

# --------------------------------------------------- gruppo D6 (12 elementi) ----
# ogni elemento = (k, f): rotazione di 60k°, f=1 → prima specchia (y→−y).
# Azione sui NOMI di ancora: flip: Vi→V(−i), Mi→M(5−i); rot k: Vi→Vi+k, Mi→Mi+k.
def act_anchor(g, name):
    k, f = g
    if name == 'C': return 'C'
    t, i = name[0], int(name[1])
    if f: i = (-i) % 6 if t == 'V' else (5-i) % 6
    return f'{t}{(i+k)%6}'
GROUP = [(k, f) for f in (0, 1) for k in range(6)]

# ------------------------------------------------------------ descrittori ----
# Un descrittore è una tupla; una tessera è un frozenset di descrittori.
#   ('seg', a, b)          segmento tra ancore (a<b)
#   ('carc', i)            arco d'angolo: centro Vi, raggio 1/2, da M(i-1) a Mi
#   ('iarc', i, k)         arco inscritto: centro C, raggio APO, da Mi a M(i+k) CCW, k=1..5
#   ('larc', i)            arco lungo: centro 2·Mi, raggio 3/2, da M(i-1) a M(i+1)
#   ('sect', mask)         mezzi-spicchi pieni: bit 2i=(C,Vi,Mi), bit 2i+1=(C,Mi,V(i+1))
#   ('bandc', mask)        bande circolari piene: 4 bit, banda j = corona tra raggio j/4 e (j+1)/4 di APO
#   ('bandh', mask)        bande esagonali piene: idem con esagoni scalati (raggio pieno = 1)
#   ('ringc'|'ringh', mask) contorni (tratto) di cerchi/esagoni ai raggi j/4 (bit j → raggio (j+1)/4)
#   ('poly', pts)          poligono generico su ancore (solo per la decodifica dell'esistente)
#   ('circ', r)            cerchio pieno generico decodificato (r quantizzato ×1000)

def act_desc(g, d):
    k, f = g
    t = d[0]
    if t == 'seg':
        a, b = act_anchor(g, d[1]), act_anchor(g, d[2])
        return ('seg',) + tuple(sorted((a, b)))
    if t == 'carc':
        i = d[1]; i = (-i) % 6 if f else i
        return ('carc', (i+k) % 6)
    if t == 'iarc':
        i, kk = d[1], d[2]
        if f: i = (5 - i - kk) % 6
        return ('iarc', (i+k) % 6, kk)
    if t == 'larc':
        i = d[1]; i = (5-i) % 6 if f else i
        return ('larc', (i+k) % 6)
    if t == 'sect':
        m = d[1]; out = 0
        for b in range(12):
            if m >> b & 1:
                nb = (11-b) if f else b
                out |= 1 << ((nb + 2*k) % 12)
        return ('sect', out)
    if t == 'poly':
        pts = tuple(act_anchor(g, p) for p in d[1])
        return ('poly', canon_cycle(pts))
    return d   # bandc/bandh/ringc/ringh/circ: D6-invarianti

def canon_cycle(pts):
    """forma canonica di un ciclo di vertici (rotazioni del ciclo + verso)."""
    best = None
    for seq in (pts, tuple(reversed(pts))):
        for s in range(len(seq)):
            cand = seq[s:] + seq[:s]
            if best is None or cand < best: best = cand
    return best

def canon(tile):
    """rappresentante canonico dell'orbita D6 di un frozenset di descrittori."""
    return min(tuple(sorted(act_desc(g, d) for d in tile)) for g in GROUP)

# ------------------------------------------------- geometria → path SVG ----
def fmt(x): return ('%.3f' % (x if abs(x) > 5e-4 else 0.0))
def P(p):   return fmt(p[0]) + ',' + fmt(p[1])

def arc_points(cx, cy, r, a0, a1, ccw=True):
    """arco campionato come polilinea (stile tiles.js: archi veri → punti)."""
    if ccw:
        while a1 <= a0 + 1e-9: a1 += 2*PI
    else:
        while a1 >= a0 - 1e-9: a1 -= 2*PI
    span = abs(a1 - a0)
    n = max(6, int(math.ceil(math.degrees(span) / 4)))
    return [(cx + r*COS(a0 + (a1-a0)*t/n), cy + r*SIN(a0 + (a1-a0)*t/n)) for t in range(n+1)]

def seg_d(a, b):        return 'M' + P(ANCHORS[a]) + 'L' + P(ANCHORS[b])
def carc_d(i):
    c = ANCHORS[f'V{i}']; p0 = ANCHORS[f'M{(i-1)%6}']; p1 = ANCHORS[f'M{i}']
    a0 = math.atan2(p0[1]-c[1], p0[0]-c[0]); a1 = math.atan2(p1[1]-c[1], p1[0]-c[0])
    # il verso giusto è quello con lo span di 120° che passa DENTRO l'esagono (raggio 1/2)
    pts = arc_points(c[0], c[1], 0.5, a0, a1, ccw=True)
    if abs((len(pts)-1)*4 - 120) > 1:                     # span sbagliato → altro verso
        pts = arc_points(c[0], c[1], 0.5, a0, a1, ccw=False)
    return 'M' + 'L'.join(P(q) for q in pts)
def iarc_d(i, k):
    a0 = PI/3*i + PI/6; a1 = PI/3*(i+k) + PI/6
    return 'M' + 'L'.join(P(q) for q in arc_points(0, 0, APO, a0, a1, ccw=True))
def larc_d(i):
    m = mco(i); c = (2*m[0], 2*m[1])
    p0 = ANCHORS[f'M{(i-1)%6}']; p1 = ANCHORS[f'M{(i+1)%6}']
    a0 = math.atan2(p0[1]-c[1], p0[0]-c[0]); a1 = math.atan2(p1[1]-c[1], p1[0]-c[0])
    pts = arc_points(c[0], c[1], 1.5, a0, a1, ccw=True)
    if max(math.hypot(q[0], q[1]) for q in pts) > 1.01:   # deve restare dentro l'esagono
        pts = arc_points(c[0], c[1], 1.5, a0, a1, ccw=False)
    return 'M' + 'L'.join(P(q) for q in pts)

# --- geometria degli archi in forma (centro, raggio, estremi) per i test di sovrapposizione
def arc_geom(d):
    if d[0] == 'carc':
        i = d[1]; return (ANCHORS[f'V{i}'], 0.5, f'M{(i-1)%6}', f'M{i}')
    if d[0] == 'larc':
        i = d[1]; m = mco(i); return ((2*m[0], 2*m[1]), 1.5, f'M{(i-1)%6}', f'M{(i+1)%6}')
    return None

HSECT = []   # vertici dei 12 mezzi-spicchi: bit 2i=(C,Vi,Mi), 2i+1=(C,Mi,V(i+1))
for i in range(6):
    HSECT.append(('C', f'V{i}', f'M{i}'))
    HSECT.append(('C', f'M{i}', f'V{(i+1)%6}'))

def sect_runs(mask):
    """i run massimali di bit consecutivi (circolari) di una maschera a 12 bit."""
    bits = [(mask >> b) & 1 for b in range(12)]
    if all(bits): return [(0, 12)]
    runs, b = [], 0
    while b < 12:
        if bits[b] and not bits[(b-1) % 12]:
            L = 0
            while bits[(b+L) % 12]: L += 1
            runs.append((b, L))
        b += 1
    return runs

def sect_d(mask):
    """path (subpath per run): C + catena di ancore lungo il bordo del run."""
    def edge_anchor(j):   # ancora di confine j (0..11): pari → V(j/2), dispari → M((j-1)/2)
        return ANCHORS[f'V{j//2}'] if j % 2 == 0 else ANCHORS[f'M{(j-1)//2}']
    out = []
    for s, L in sect_runs(mask):
        pts = [(0.0, 0.0)] + [edge_anchor((s+t) % 12) for t in range(L+1)]
        out.append('M' + 'L'.join(P(q) for q in pts) + 'Z')
    return ''.join(out)

RADII_C = [APO*0.25, APO*0.5, APO*0.75, APO]     # bande circolari
RADII_H = [0.25, 0.5, 0.75, 1.0]                 # bande esagonali (esagoni scalati)
def circle_d(r):
    return 'M' + 'L'.join(P(q) for q in arc_points(0, 0, r, 0, 2*PI)) + 'Z'
def hexring_d(s):
    return 'M' + 'L'.join(P((vco(i)[0]*s, vco(i)[1]*s)) for i in range(6)) + 'Z'

def band_parts(mask, radii, shape_d):
    """bande piene: ogni banda j (tra raggio j e j+1, raggio 0 = centro) come
       corona even-odd; bande adiacenti si fondono in un'unica corona."""
    filled = [(mask >> j) & 1 for j in range(4)]
    parts, j = [], 0
    while j < 4:
        if filled[j]:
            L = 0
            while j+L < 4 and filled[j+L]: L += 1
            d = shape_d(radii[j+L-1])
            if j > 0: d += shape_d(radii[j-1])
            parts.append({'d': d, 'eo': 1})
            j += L
        else: j += 1
    return parts

# =================================================================== FAMIGLIE ===
def fam_settori():
    excl = set()
    # fette già in libreria (ge_00..ge_06): run singolo di lunghezza L che parte
    # da un bordo di spicchio (pari); L=1 anche dispari (stessa orbita).
    for L, par in [(1, None), (2, 0), (4, 0), (6, 0), (8, 0), (12, 0)]:
        for s in range(12):
            if par is not None and s % 2 != par: continue
            m = 0
            for t in range(L): m |= 1 << ((s+t) % 12)
            excl.add(canon(frozenset([('sect', m)])))
    seen, out = set(), []
    for m in range(1, 4096):
        c = canon(frozenset([('sect', m)]))
        if c in seen or c in excl: continue
        seen.add(c); out.append((c, [{'d': sect_d(c[0][1]), 'eo': 0}]))
    return out

def seg_vocab():
    names = sorted(ANCHORS)
    vocab = []
    for a, b in itertools.combinations(names, 2):
        # esclusi i segmenti che GIACCIONO sul bordo (Vi–Mi, Mi–Vi+1, Vi–Vi+1)
        onb = False
        for i in range(6):
            edge = {f'V{i}', f'M{i}', f'V{(i+1)%6}'}
            if a in edge and b in edge: onb = True
        if not onb: vocab.append(('seg', a, b))
    return vocab

def fam_corde(existing):
    """due pack: corde (1-2 segmenti + triple CONNESSE = figure) e
       corde-libere (triple sconnesse = texture)."""
    vocab = seg_vocab()                                   # 60 segmenti
    seen, out, out_free = set(), [], []
    def push(desc_set, dest):
        c = canon(frozenset(desc_set))
        if c in seen or c in existing: return
        seen.add(c)
        dest.append((c, [{'d': seg_d(d[1], d[2]), 'sw': 0.34} for d in c]))
    for s in vocab: push([s], out)
    for pair in itertools.combinations(vocab, 2): push(pair, out)
    for tri in itertools.combinations(vocab, 3):
        es = [set(d[1:]) for d in tri]
        g01, g02, g12 = es[0] & es[1], es[0] & es[2], es[1] & es[2]
        connected = (g01 or g02) and (g01 or g12) and (g02 or g12)
        push(tri, out if connected else out_free)
    return out, out_free

def arcs_compatible(a, b):
    """niente doppioni visivi: archi sullo stesso cerchio mai sovrapposti né adiacenti."""
    if a[0] == 'iarc' and b[0] == 'iarc':
        ia, ka = a[1], a[2]; ib, kb = b[1], b[2]
        sa = {(ia+t) % 6 for t in range(ka+1)}            # metà-lato toccati
        sb = {(ib+t) % 6 for t in range(kb+1)}
        return not (sa & sb)                              # disgiunti anche negli estremi
    ga, gb = arc_geom(a), arc_geom(b)
    if ga and gb and max(abs(ga[0][0]-gb[0][0]), abs(ga[0][1]-gb[0][1])) < 1e-9:
        return False                                      # stesso cerchio (carc/larc): mai due
    return True

def fam_archi(existing):
    vocab = ([('carc', i) for i in range(6)] +
             [('iarc', i, k) for i in range(6) for k in range(1, 6)] +
             [('larc', i) for i in range(6)])
    def d_of(d):
        if d[0] == 'carc': return carc_d(d[1])
        if d[0] == 'iarc': return iarc_d(d[1], d[2])
        return larc_d(d[1])
    seen, out = set(), []
    def push(ds):
        c = canon(frozenset(ds))
        if c in seen or c in existing: return
        seen.add(c)
        out.append((c, [{'d': d_of(d), 'sw': 0.34} for d in c]))
    for a in vocab: push([a])
    for a, b in itertools.combinations(vocab, 2):
        if arcs_compatible(a, b): push([a, b])
    for tri in itertools.combinations(vocab, 3):
        if all(arcs_compatible(x, y) for x, y in itertools.combinations(tri, 2)):
            push(tri)
    return out

def fam_anelli(existing):
    seen, out = set(), []
    for kind, radii, shape in [('bandc', RADII_C, circle_d), ('bandh', RADII_H, hexring_d)]:
        for m in range(1, 16):
            c = canon(frozenset([(kind, m)]))
            if c in seen or c in existing: continue
            seen.add(c); out.append((c, band_parts(m, radii, shape)))
    for kind, radii, shape in [('ringc', RADII_C, circle_d), ('ringh', RADII_H, hexring_d)]:
        for m in range(1, 16):
            if kind == 'ringh' and m >> 3 & 1: continue   # contorno esagono pieno = bordo cella, inutile
            c = canon(frozenset([(kind, m)]))
            if c in seen or c in existing: continue
            seen.add(c)
            out.append((c, [{'d': shape(radii[j]), 'sw': 0.34} for j in range(4) if m >> j & 1]))
    return out

# ============================================= DECODIFICA di tiles.js esistente ===
def parse_path(d):
    """path → lista di subpath [ [(x,y)...], ... ]; C flattenata; True se chiusa."""
    toks = re.findall(r'([MLCZz])|(-?\d*\.?\d+(?:e-?\d+)?)', d)
    vals, cmds = [], []
    cur = None; sub = []; subs = []; closed = []
    i = 0
    flat = re.findall(r'[MLCZz]|-?\d*\.?\d+(?:e-?\d+)?', d)
    while i < len(flat):
        t = flat[i]
        if t in 'MLCZz':
            cmd = t; i += 1
            if cmd in 'Zz':
                if sub: subs.append(sub); closed.append(True); sub = []
                continue
            if cmd == 'M' and sub:
                subs.append(sub); closed.append(False); sub = []
        else:
            cmd = cmds[-1] if cmds else 'L'
        cmds.append(cmd)
        if cmd in 'ML':
            x, y = float(flat[i]), float(flat[i+1]); i += 2
            sub.append((x, y)); cur = (x, y)
        elif cmd == 'C':
            x1, y1, x2, y2, x, y = (float(flat[i+j]) for j in range(6)); i += 6
            p0 = cur
            for t2 in range(1, 13):                       # bézier → 12 segmenti
                u = t2/12; v = 1-u
                sub.append((v**3*p0[0] + 3*v*v*u*x1 + 3*v*u*u*x2 + u**3*x,
                            v**3*p0[1] + 3*v*v*u*y1 + 3*v*u*u*y2 + u**3*y))
            cur = (x, y)
    if sub: subs.append(sub); closed.append(False)
    return subs, closed

def snap_anchor(p, tol=0.02):
    for n, q in ANCHORS.items():
        if math.hypot(p[0]-q[0], p[1]-q[1]) < tol: return n
    return None

def fit_arc(pts):
    """se i punti stanno su un cerchio → (centro, raggio), altrimenti None."""
    if len(pts) < 3: return None
    (x1, y1), (x2, y2), (x3, y3) = pts[0], pts[len(pts)//2], pts[-1]
    d = 2*(x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2))
    if abs(d) < 1e-9: return None
    ux = ((x1*x1+y1*y1)*(y2-y3) + (x2*x2+y2*y2)*(y3-y1) + (x3*x3+y3*y3)*(y1-y2)) / d
    uy = ((x1*x1+y1*y1)*(x3-x2) + (x2*x2+y2*y2)*(x1-x3) + (x3*x3+y3*y3)*(x2-x1)) / d
    r = math.hypot(x1-ux, y1-uy)
    if all(abs(math.hypot(px-ux, py-uy) - r) < 0.02 for px, py in pts):
        return ((ux, uy), r)
    return None

def collinear(pts):
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    L = math.hypot(x2-x1, y2-y1)
    if L < 1e-9: return False
    return all(abs((x2-x1)*(y1-py) - (x1-px)*(y2-y1))/L < 0.02 for px, py in pts)

def decode_stroke(sub):
    """polilinea → descrittore seg/carc/iarc/larc, se riconoscibile."""
    a, b = snap_anchor(sub[0]), snap_anchor(sub[-1])
    if len(sub) == 2 or collinear(sub):
        if a and b and a != b: return ('seg',) + tuple(sorted((a, b)))
        return None
    fit = fit_arc(sub)
    if not fit or not a or not b: return None
    (cx, cy), r = fit
    if abs(r-0.5) < 0.03:
        for i in range(6):
            v = vco(i)
            if math.hypot(cx-v[0], cy-v[1]) < 0.03 and {a, b} == {f'M{(i-1)%6}', f'M{i}'}:
                return ('carc', i)
    if abs(r-APO) < 0.03 and math.hypot(cx, cy) < 0.03 and a[0] == 'M' and b[0] == 'M':
        ia, ib = int(a[1]), int(b[1])
        mid = sub[len(sub)//2]; am = math.atan2(mid[1], mid[0])
        for i, k in [(ia, (ib-ia) % 6), (ib, (ia-ib) % 6)]:
            k = k or 6
            if k > 5: continue
            a0 = PI/3*i + PI/6
            span = (am - a0) % (2*PI)
            if span < PI/3*k + 1e-3:                      # il punto medio cade nell'arco CCW
                return ('iarc', i, k)
    if abs(r-1.5) < 0.03:
        for i in range(6):
            m = mco(i)
            if math.hypot(cx-2*m[0], cy-2*m[1]) < 0.03 and {a, b} == {f'M{(i-1)%6}', f'M{(i+1)%6}'}:
                return ('larc', i)
    return None

def decode_fill(sub, closed):
    """subpath chiusa → poligono su ancore, maschera di settori o cerchio."""
    pts = sub[:-1] if len(sub) > 1 and math.hypot(sub[0][0]-sub[-1][0], sub[0][1]-sub[-1][1]) < 1e-6 else sub
    names = [snap_anchor(p) for p in pts]
    if all(names):
        dedup = [n for j, n in enumerate(names) if n != names[j-1]]
        return ('poly', canon_cycle(tuple(dedup)))
    fit = fit_arc(pts)
    if fit and math.hypot(fit[0][0], fit[0][1]) < 0.02:
        return ('circ', round(fit[1]*1000))
    return None

def poly_to_sect(desc):
    """se un poligono decodificato è C+catena di bordo → maschera settori (per confronto)."""
    if desc[0] != 'poly': return desc
    pts = desc[1]
    if 'C' not in pts: return desc
    i = pts.index('C'); chain = pts[i+1:] + pts[:i]
    def bidx(n): return int(n[1])*2 if n[0] == 'V' else int(n[1])*2+1
    idx = [bidx(n) for n in chain]
    rev = list(reversed(idx))
    for seq in (idx, rev):
        if all((seq[j+1]-seq[j]) % 12 == 1 for j in range(len(seq)-1)):
            m = 0
            for j in range(len(seq)-1): m |= 1 << (seq[j] % 12)
            return ('sect', m)
    return desc

def decode_existing():
    src = open(os.path.join(ROOT, 'tiles.js')).read()
    body = src[src.index('['): src.rindex(']')+1]
    body = re.sub(r',\s*\]', ']', body)        # virgola finale tollerata da JS, non da JSON
    data = json.loads(body)
    existing, undecoded = set(), []
    for t in data:
        descs, ok = [], True
        for part in t['parts']:
            subs, closed = parse_path(part['d'])
            for s, c in zip(subs, closed):
                d = decode_stroke(s) if part.get('sw') else decode_fill(s, c)
                if d is None: ok = False; break
                descs.append(poly_to_sect(d))
            if not ok: break
        if ok and descs: existing.add(canon(frozenset(descs)))
        else: undecoded.append(t['id'])
    return existing, undecoded, len(data)

# ======================================================================= MAIN ===
PREFIX = {'settori': 'st', 'corde': 'cr', 'corde-libere': 'cl', 'archi': 'ar', 'anelli': 'an'}
ALL_IDS = set()
def tile_id(key, c):
    return PREFIX[key] + '_' + hashlib.md5(repr(c).encode()).hexdigest()[:8]

def emit_pack(key, name, cat, tiles):
    arr = []
    for c, parts in tiles:
        tid = tile_id(key, c)
        assert tid not in ALL_IDS, 'collisione id ' + tid
        ALL_IDS.add(tid)
        arr.append({'id': tid, 'cat': cat, 'parts': parts})
    body = ',\n  '.join(json.dumps(t, separators=(',', ':'), ensure_ascii=False) for t in arr)
    js = ("window.TILE_PACKS=window.TILE_PACKS||{};\n"
          f"window.TILE_PACKS[{json.dumps(key)}]={{name:{json.dumps(name)},tiles:[\n  {body}\n]}};\n")
    path = os.path.join(ROOT, 'packs', key + '.js')
    open(path, 'w').write(js)
    return len(arr), os.path.getsize(path)

def emit_preview(key, name):
    html = f"""<!doctype html><meta charset=utf-8><title>Pack {name} — anteprima</title>
<style>body{{font:13px/1.4 monospace;background:#f4f1ea;color:#222;margin:20px}}
.g{{display:flex;flex-wrap:wrap;gap:8px}} .t{{background:#fff;border:1px solid #ddd;padding:6px;text-align:center}}
.t small{{display:block;opacity:.55;margin-top:2px;font-size:9px}}</style>
<h2>Pack «{name}» <span id=n></span></h2><div class=g id=g></div>
<script src="{key}.js"></script><script>
const P=window.TILE_PACKS[{json.dumps(key)}];document.getElementById('n').textContent='— '+P.tiles.length+' tessere';
const hex='M1,0L0.5,0.866L-0.5,0.866L-1,0L-0.5,-0.866L0.5,-0.866Z';
document.getElementById('g').innerHTML=P.tiles.map(t=>{{
 const parts=t.parts.map(p=>p.sw?`<path d="${{p.d}}" fill="none" stroke="#111" stroke-width=".13" stroke-linecap="round"/>`
  :`<path d="${{p.d}}" fill="#111"${{p.eo?' fill-rule="evenodd"':''}}/>`).join('');
 return `<div class=t><svg width=64 height=58 viewBox="-1.05 -0.95 2.1 1.9"><path d="${{hex}}" fill="none" stroke="#ccc" stroke-width=".02"/>${{parts}}</svg><small>${{t.id}}</small></div>`;
}}).join('');
</script>"""
    open(os.path.join(ROOT, 'packs', 'anteprima-' + key + '.html'), 'w').write(html)

def main():
    census_only = '--census' in sys.argv
    existing, undecoded, ntot = decode_existing()
    print(f'tiles.js: {ntot} tessere, {len(existing)} decodificate come descrittori, '
          f'{len(undecoded)} non decodificabili (forme libere, ok): {" ".join(undecoded[:8])}…')

    corde, corde_libere = fam_corde(existing)
    fams = [
        ('settori',      'Settori',      'Pack · Settori',      fam_settori()),
        ('corde',        'Corde',        'Pack · Corde',        corde),
        ('corde-libere', 'Corde libere', 'Pack · Corde libere', corde_libere),
        ('archi',        'Archi',        'Pack · Archi',        fam_archi(existing)),
        ('anelli',       'Anelli',       'Pack · Anelli',       fam_anelli(existing)),
    ]
    print('\nCENSIMENTO')
    for key, name, cat, tiles in fams:
        print(f'  {name:<9} {len(tiles):>6} tessere canoniche')
    print(f'  {"TOTALE":<9} {sum(len(t) for *_, t in fams):>6}')
    if census_only: return

    os.makedirs(os.path.join(ROOT, 'packs'), exist_ok=True)
    manifest = []
    for key, name, cat, tiles in fams:
        n, size = emit_pack(key, name, cat, tiles)
        emit_preview(key, name)
        manifest.append({'key': key, 'file': 'packs/' + key + '.js', 'name': name, 'count': n})
        print(f'  scritto packs/{key}.js ({n} tessere, {size//1024} KB) + anteprima-{key}.html')
    open(os.path.join(ROOT, 'packs', 'manifest.js'), 'w').write(
        'window.TILE_PACK_INDEX=' + json.dumps(manifest, ensure_ascii=False) + ';\n')
    print('  scritto packs/manifest.js')

if __name__ == '__main__':
    # sanity: il gruppo è chiuso e l'azione preserva le distanze tra ancore
    for g in GROUP:
        for n, p in ANCHORS.items():
            q = ANCHORS[act_anchor(g, n)]
            assert abs(math.hypot(*p) - math.hypot(*q)) < 1e-9, (g, n)
    main()
