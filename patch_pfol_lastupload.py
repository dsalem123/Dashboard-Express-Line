"""
patch_pfol_lastupload.py
Agrega badge "Últ. carga" arriba a la derecha de cada cliente en Portfolios Online.
"""
import json, re, sys

FILE = 'crm_offshore_cambios.html'

with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

# Localizar línea del blob de portfolios
pfol_blob_idx = None
for i, l in enumerate(lines):
    if 'portfolios-frame' in l and 'URL.createObjectURL(blob)' in l:
        pfol_blob_idx = i - 2
        break

if pfol_blob_idx is None:
    print('ERROR: no se encontró el blob de portfolios-frame')
    sys.exit(1)

blob_line = lines[pfol_blob_idx]
m = re.match(r'(\s*var _c=)(\".*\");', blob_line)
if not m:
    print('ERROR: línea del blob no tiene el formato esperado')
    sys.exit(1)

blob_str = json.loads(m.group(2))
original_blob = blob_str

# ── 1. CSS: agregar .card-upload-badge ──
OLD_CSS = '.card-date{font-size:10px;color:var(--vg);margin-top:10px;letter-spacing:.3px;}'
NEW_CSS = (
    '.card-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;}'
    '.card-upload-badge{font-size:9px;color:var(--vg);text-align:right;white-space:nowrap;'
    'flex-shrink:0;line-height:1.5;padding-top:1px;}'
    '.card-upload-badge span{display:block;font-size:8px;letter-spacing:1px;'
    'text-transform:uppercase;color:rgba(168,218,187,.35);margin-bottom:1px;}'
    '.card-date{font-size:10px;color:var(--vg);margin-top:10px;letter-spacing:.3px;}'
)

if '.card-upload-badge' in blob_str:
    print('CSS ya aplicado — saltando paso 1')
elif OLD_CSS not in blob_str:
    print('ERROR: no se encontró .card-date CSS')
    sys.exit(1)
else:
    blob_str = blob_str.replace(OLD_CSS, NEW_CSS, 1)
    print('OK Paso 1: CSS .card-upload-badge agregado')

# ── 2. Modificar template del card en renderGrid ──
OLD_CARD_HEADER = '<div class="card-name">${c.name}</div>'
NEW_CARD_HEADER = (
    '<div class="card-top">'
    '<div class="card-name">${c.name}</div>'
    '<div class="card-upload-badge">'
    '<span>\\u00dalt. carga</span>'
    '${c.lastUpdated||\'Sin archivos\'}'
    '</div>'
    '</div>'
)

if 'card-upload-badge' in blob_str and 'card-top' in blob_str and OLD_CARD_HEADER not in blob_str:
    print('Template ya aplicado — saltando paso 2')
elif OLD_CARD_HEADER not in blob_str:
    print('ERROR: no se encontró card-name en el template')
    sys.exit(1)
else:
    blob_str = blob_str.replace(OLD_CARD_HEADER, NEW_CARD_HEADER, 1)
    print('OK Paso 2: badge de última carga en header del card')

# ── Serializar y guardar ──
if blob_str == original_blob:
    print('\nNada cambió — el patch ya estaba aplicado.')
    sys.exit(0)

new_blob_json = json.dumps(blob_str).replace('</', '<\\/')
lines[pfol_blob_idx] = m.group(1) + new_blob_json + ';'
html = '\n'.join(lines)

assert '.card-upload-badge' in html
assert 'Últ. carga' in html or '\\u00dalt. carga' in html

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nListo — {FILE} actualizado.')
