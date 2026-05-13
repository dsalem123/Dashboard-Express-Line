"""
sync_index.py — Copia crm_offshore_cambios.html -> index.html
preservando el <script id="crm-snapshot"> del index.html REMOTO (origin/master).

Usa git show origin/master:index.html para leer el snapshot real de Vercel,
no el index.html local que puede estar desactualizado.
"""
import re, sys, subprocess

SRC  = 'crm_offshore_cambios.html'
DEST = 'index.html'

SNAP_RE = r'<script type="application/json" id="crm-snapshot">[\s\S]*?</script>'

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()

# Intentar leer index.html desde el remoto para obtener el snapshot mas reciente
dest = None
try:
    result = subprocess.run(
        ['git', 'show', 'origin/master:index.html'],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode == 0 and result.stdout.strip():
        dest = result.stdout
        print('Snapshot leido desde origin/master:index.html (remoto).')
except Exception:
    pass

# Fallback al archivo local si el remoto no esta disponible
if not dest:
    try:
        with open(DEST, 'r', encoding='utf-8') as f:
            dest = f.read()
        print('AVISO: no se pudo leer remoto, usando index.html local.')
    except FileNotFoundError:
        dest = None

dest_snap = re.search(SNAP_RE, dest) if dest else None
src_snap  = re.search(SNAP_RE, src)

if dest_snap and src_snap:
    out = re.sub(SNAP_RE, dest_snap.group(0), src, count=1)
    print('Snapshot preservado.')
elif src_snap:
    out = src
    print('AVISO: sin snapshot remoto — se usa el de la fuente.')
else:
    print('ERROR: crm_offshore_cambios.html no tiene id="crm-snapshot".')
    sys.exit(1)

with open(DEST, 'w', encoding='utf-8') as f:
    f.write(out)
print(f'OK — {DEST} actualizado ({len(out)} chars).')
