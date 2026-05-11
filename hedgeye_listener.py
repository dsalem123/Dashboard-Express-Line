"""
CRM Listener — dos funciones en paralelo:
1. localhost:5055/snapshot  — recibe datos del CRM y los sube a Vercel via GitHub
2. ntfy.sh                  — trigger remoto para ejecutar el scraper de Hedgeye
Para iniciar: python hedgeye_listener.py
"""
import json, os, re, subprocess, sys, datetime, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)
    import requests

TOPIC = 'crm-hg-dsalem123-offshore'
PORT  = 5055
BASE  = os.path.dirname(os.path.abspath(__file__))

# ── Resumen de secciones (misma lógica que hedgeye_server.py) ─────────────────

_TS_RE = re.compile(r'\s*\(\d+:\d+(?:[,\s]+\d+:\d+)*\)\s*$')
_MID_ATTR = re.compile(
    r',?\s+y\s+(dijo|agregó|añadió|señaló|reiteró|aclaró|explicó|describió|destacó)\s+(que\s+)?',
    re.IGNORECASE)
_DICIENDO = re.compile(r',?\s+diciendo\s+que\s+', re.IGNORECASE)
_SEGUN = re.compile(r',?\s*según\s+(él|ella|Keith|McCullough)\b[,]?\s*', re.IGNORECASE)
_REITERO_CITA = re.compile(r'\w+:\s*[«"\'](.*?)[»"\']', re.IGNORECASE)
_NAMES_RE = r'Keith|McCullough'
_VERBS_IMPL = (r'Dijo|Señaló|Reiteró|Agregó|Explicó|Destacó|Enfatizó|Añadió|Mencionó|'
               r'Citó|Afirmó|Indicó|Advirtió|Apuntó|Comentó|Subrayó|Reforzó|Recordó|'
               r'Reconoció|Rechazó|Insistió|Precisó|Sostuvo|Hizo')

def _limpiar_atribucion(texto):
    m = re.match(rf'({_NAMES_RE})\s+\S+\s+que\s+', texto, re.IGNORECASE)
    if m:
        r = texto[m.end()]; return (r.upper() + texto[m.end()+1:]) if r else ''
    m2 = re.match(rf'({_NAMES_RE})\s+\S+(?:\s+con)?\s+[^,]+,\s*', texto, re.IGNORECASE)
    if m2:
        r = texto[m2.end():]; return (r[0].upper() + r[1:]) if r else ''
    m3 = re.match(rf'({_VERBS_IMPL})\s+que\s+', texto, re.IGNORECASE)
    if m3:
        r = texto[m3.end():]; return (r[0].upper() + r[1:]) if r else ''
    m4 = re.match(r'Hizo\s+hincapi[eé]\s+en\s+que\s+', texto, re.IGNORECASE)
    if m4:
        r = texto[m4.end():]; return (r[0].upper() + r[1:]) if r else ''
    return texto

def _limpiar_inline(texto):
    t = _MID_ATTR.sub('. ', texto)
    t = _DICIENDO.sub('. ', t)
    t = _SEGUN.sub(' ', t)
    t = re.sub(r',?\s+pero\s+(' + _VERBS_IMPL + r')\s+que\s+', '. ', t, flags=re.IGNORECASE)
    t = re.sub(rf'\s+y\s+({_VERBS_IMPL}):\s*[«"\']?(.*?)[»"\']?(?=\.|,|$)', r'. \2', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+y\s+[«"](.*?)[»"]', r'. \1', t)
    t = _REITERO_CITA.sub(lambda m: m.group(1), t)
    t = re.sub(r'\s+y\s+que\s+', ' y ', t)
    t = re.sub(r'\.\s*\.\s*', '. ', t)
    return t

def _limpiar_gerundio(texto):
    m = re.match(r'[A-ZÁÉÍÓÚÑ]\w+(?:ando|iendo)\s+que\s+', texto, re.IGNORECASE)
    if m:
        r = texto[m.end():]; return (r[0].upper() + r[1:]) if r else texto
    return texto

def _primera_oracion(texto, max_chars=400):
    for sep in ('. ', '.\n'):
        idx = texto.find(sep)
        if 0 < idx <= max_chars:
            return texto[:idx + 1].strip()
    colon_idx = texto.find(': ')
    if 60 < colon_idx < max_chars:
        return texto[:colon_idx] + '.'
    trunc = texto[:max_chars]
    last_dot = trunc.rfind('.')
    if last_dot > 60:
        return texto[:last_dot + 1].strip()
    return trunc.rstrip(' ,;') + '…'

def _resumir_seccion(puntos):
    oraciones = []
    for p in puntos[:3]:
        t = _TS_RE.sub('', p.strip()).strip()
        t = _limpiar_atribucion(t)
        t = _limpiar_gerundio(t)
        t = _limpiar_inline(t)
        t = re.sub(r'\s{2,}', ' ', t).strip()
        primera = _primera_oracion(t)
        if len(primera) > 35:
            oraciones.append(primera)
        if len(oraciones) >= 2:
            break
    return ' '.join(oraciones)

def ts():
    return datetime.datetime.now().strftime('%H:%M:%S')

# ── HTML helpers ──────────────────────────────────────────────────────────────

def update_html_files(state_json, hg_json=None):
    for fname in ['crm_offshore_cambios.html', 'index.html']:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        updated = re.sub(
            r'<script type="application/json" id="crm-snapshot">[\s\S]*?<\/script>',
            f'<script type="application/json" id="crm-snapshot">{state_json}</script>',
            content, count=1
        )
        if hg_json:
            updated = re.sub(
                r'const HG_STATIC_DATA = (?:null|\{[\s\S]*?\});',
                f'const HG_STATIC_DATA = {hg_json};',
                updated, count=1
            )
        if updated == content:
            print(f'  AVISO: no se encontro crm-snapshot en {fname}')
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f'[{ts()}] {fname} actualizado')

# ── git push ──────────────────────────────────────────────────────────────────

def git_push(msg):
    os.chdir(BASE)
    subprocess.run(['git', 'add', 'crm_offshore_cambios.html', 'index.html'])
    r = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True)
    if 'nothing to commit' in r.stdout:
        print(f'[{ts()}] Sin cambios nuevos')
        return
    r2 = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if r2.returncode == 0:
        print(f'[{ts()}] Push OK — Vercel actualiza en ~30 segundos')
        return
    # Push rechazado — el remoto está adelante, hacer fetch + merge + re-push
    print(f'[{ts()}] Push rechazado, haciendo merge con remoto...')
    subprocess.run(['git', 'fetch'])
    merge = subprocess.run(['git', 'merge', 'origin/master', '--no-edit'], capture_output=True, text=True)
    if merge.returncode != 0:
        # Conflicto en merge — usar crm_offshore_cambios.html como fuente de verdad
        print(f'[{ts()}] Conflicto en merge — resolviendo con crm_offshore_cambios.html')
        import shutil
        shutil.copy('crm_offshore_cambios.html', 'index.html')
        subprocess.run(['git', 'add', 'crm_offshore_cambios.html', 'index.html'])
        subprocess.run(['git', 'commit', '-m', f'{msg} (merge conflict resolved)'])
    r3 = subprocess.run(['git', 'push'])
    if r3.returncode == 0:
        print(f'[{ts()}] Push OK (tras merge) — Vercel actualiza en ~30 segundos')
    else:
        print(f'[{ts()}] Error en git push tras merge')

# ── Hedgeye scraper ───────────────────────────────────────────────────────────

def handle_hedgeye_trigger():
    print(f'[{ts()}] Ejecutando scraper de Hedgeye...')
    result = subprocess.run([sys.executable, os.path.join(BASE, 'hedgeye_scraper.py')], timeout=300)
    if result.returncode != 0:
        print(f'[{ts()}] Scraper fallo'); return
    print(f'[{ts()}] Scraper OK')
    data_file = os.path.join(BASE, 'hedgeye_data.json')
    hg_json = None
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Calcular resúmenes por sección y guardarlos en el JSON
        secciones = data.get('macro_show', {}).get('secciones', [])
        changed = False
        for sec in secciones:
            if sec.get('puntos') and not sec.get('resumen'):
                sec['resumen'] = _resumir_seccion(sec['puntos'])
                changed = True
        if changed:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            print(f'[{ts()}] Resúmenes calculados para {len(secciones)} secciones')
        hg_json = json.dumps(data, ensure_ascii=False)
    update_html_files(state_json=None, hg_json=hg_json)
    git_push(f'Hedgeye update {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}')

def update_html_files(state_json=None, hg_json=None):
    for fname in ['crm_offshore_cambios.html', 'index.html']:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        updated = content
        if state_json is not None:
            updated = re.sub(
                r'<script type="application/json" id="crm-snapshot">[\s\S]*?<\/script>',
                f'<script type="application/json" id="crm-snapshot">{state_json}</script>',
                updated, count=1
            )
        if hg_json is not None:
            updated = re.sub(
                r'const HG_STATIC_DATA = (?:null|\{[\s\S]*?\});',
                f'const HG_STATIC_DATA = {hg_json};',
                updated, count=1
            )
        if updated == content:
            print(f'  AVISO: sin cambios en {fname}')
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f'[{ts()}] {fname} actualizado')

# ── HTTP server ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200); self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers(); self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path != '/snapshot':
            self.send_response(404); self.end_headers(); return
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            state  = json.loads(body)
            # Extraer hgData del state antes de guardarlo en crm-snapshot
            hg_json = None
            hg_raw  = state.pop('_hgData', None)
            if hg_raw:
                hg_json = json.dumps(hg_raw, ensure_ascii=False)
            state_json = json.dumps(state, ensure_ascii=False)
            print(f'\n[{ts()}] Snapshot recibido desde el CRM')
            update_html_files(state_json=state_json, hg_json=hg_json)
            git_push(f'CRM snapshot {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}')
            self.send_response(200); self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers(); self.wfile.write(b'{"ok":true}')
            print(f'\nEsperando proximo trigger...')
        except Exception as e:
            print(f'[{ts()}] Error: {e}')
            self.send_response(500); self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

# ── ntfy.sh listener ──────────────────────────────────────────────────────────

def listen_ntfy():
    url = f'https://ntfy.sh/{TOPIC}/json'
    while True:
        try:
            with requests.get(url, stream=True, timeout=None) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            msg = json.loads(line)
                            if msg.get('event') == 'message':
                                print(f'\n[{ts()}] Trigger Hedgeye recibido!')
                                handle_hedgeye_trigger()
                                print(f'\nEsperando proximo trigger...')
                        except Exception as e:
                            print(f'Error ntfy: {e}')
        except Exception as e:
            print(f'[{ts()}] ntfy desconectado ({e}) — reconectando...')
            time.sleep(5)

# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=' * 55)
    print('  CRM Listener — ExpressLine')
    print(f'  Snapshot:  http://localhost:{PORT}/snapshot')
    print(f'  Hedgeye:   ntfy.sh/{TOPIC}')
    print('  Mantene esta ventana abierta.')
    print('=' * 55)
    threading.Thread(target=lambda: HTTPServer(('127.0.0.1', PORT), Handler).serve_forever(), daemon=True).start()
    print(f'[{ts()}] Servidor local activo en puerto {PORT}')
    listen_ntfy()
