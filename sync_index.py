"""
sync_index.py — Copia crm_offshore_cambios.html -> index.html
preservando el <script id="crm-snapshot"> del index.html existente.

USAR ESTE SCRIPT en lugar de: cp crm_offshore_cambios.html index.html
"""
import re, sys

SRC  = 'crm_offshore_cambios.html'
DEST = 'index.html'

with open(SRC,  'r', encoding='utf-8') as f: src  = f.read()
with open(DEST, 'r', encoding='utf-8') as f: dest = f.read()

SNAP_RE = r'<script type="application/json" id="crm-snapshot">[\s\S]*?</script>'

dest_snap = re.search(SNAP_RE, dest)
src_snap  = re.search(SNAP_RE, src)

if dest_snap and src_snap:
    # Preserve the snapshot from index.html (has user data)
    out = re.sub(SNAP_RE, dest_snap.group(0), src, count=1)
    print('Snapshot preservado de index.html existente.')
elif src_snap:
    out = src
    print('AVISO: index.html sin snapshot — se usa el de la fuente.')
else:
    print('ERROR: crm_offshore_cambios.html no tiene id="crm-snapshot".')
    sys.exit(1)

with open(DEST, 'w', encoding='utf-8') as f: f.write(out)
print(f'OK — {DEST} actualizado ({len(out)} chars).')
