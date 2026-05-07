"""
Hedgeye Server — scrapes app.hedgeye.com daily at 13:00 ART
Serves data via REST API at localhost:5050

Requirements: pip install flask flask-cors apscheduler playwright
              playwright install chromium
"""
import json, os, logging, datetime, subprocess, sys, re
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app   = Flask(__name__)
CORS(app)
log   = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

BASE   = os.path.dirname(os.path.abspath(__file__))
CFG    = os.path.join(BASE, 'hedgeye_config.json')
DATA   = os.path.join(BASE, 'hedgeye_data.json')
DBG    = os.path.join(BASE, 'hedgeye_debug')

os.makedirs(DBG, exist_ok=True)

# ── helpers ─────────────────────────────────────────────────────────────────

def load_config():
    with open(CFG, encoding='utf-8') as f:
        return json.load(f)

def save_data(d):
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_data():
    if os.path.exists(DATA):
        with open(DATA, encoding='utf-8') as f:
            return json.load(f)
    return None

# ── scraper ──────────────────────────────────────────────────────────────────

def scrape_hedgeye():
    log.info("=== Hedgeye scrape START (subprocess) ===")
    scraper = os.path.join(BASE, 'hedgeye_scraper.py')
    result = subprocess.run(
        [sys.executable, scraper],
        capture_output=True, text=True, timeout=180
    )
    log.info(f"Scraper stdout: {result.stdout}")
    if result.returncode != 0:
        log.error(f"Scraper stderr: {result.stderr}")
    d = load_data()
    if d:
        return d
    return {'error': result.stderr[-300:] if result.stderr else 'Unknown error',
            'bullish': [], 'bearish': [], 'macro_show': {}, 'updated': None}

def _unused_scrape_hedgeye():
    cfg = load_config()

    data = {
        "updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        "bullish": [],
        "bearish": [],
        "macro_show": {"title": "", "date": "", "bullets": []},
        "risk_ranges": [],
        "error": None
    }

    try:
        pw = sync_playwright().start()
        try:
            browser = pw.chromium.launch(
                headless=False,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled',
                      '--disable-web-security']
            )
            ctx = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                viewport={'width': 1440, 'height': 900},
                locale='en-US'
            )
            ctx.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            )
            page = ctx.new_page()

            # ── LOGIN ────────────────────────────────────────────────────────
            log.info("Logging in...")
            page.goto('https://app.hedgeye.com/users/sign_in', wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            page.screenshot(path=os.path.join(DBG, '01_login.png'))

            page.fill('input[id="user_email"], input[name="user[email]"], input[type="email"]', cfg['email'])
            page.fill('input[id="user_password"], input[name="user[password]"], input[type="password"]', cfg['password'])
            page.click('input[type="submit"], button[type="submit"], .btn-submit, [value="Sign in"]')
            page.wait_for_load_state('networkidle', timeout=20000)
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(DBG, '02_after_login.png'))
            log.info(f"After login URL: {page.url}")

            if 'sign_in' in page.url:
                data['error'] = 'Login failed — check credentials in hedgeye_config.json'
                browser.close()
                pw.stop()
                save_data(data)
                return data

            # ── POSITIONS / SIGNALS ──────────────────────────────────────────
            log.info("Scraping positions...")
            for url in ['https://app.hedgeye.com/positions',
                        'https://app.hedgeye.com/signals',
                        'https://app.hedgeye.com/risk_ranges']:
                page.goto(url, wait_until='networkidle', timeout=20000)
                page.wait_for_timeout(3000)
                page.screenshot(path=os.path.join(DBG, f'03_positions_{url.split("/")[-1]}.png'))
                log.info(f"Positions page ({url}) loaded, saving HTML for debug")
                with open(os.path.join(DBG, f'positions_{url.split("/")[-1]}.html'), 'w', encoding='utf-8') as fh:
                    fh.write(page.content())
                if 'not found' not in page.title().lower() and page.url == url:
                    break

            # Extract rows — generic approach, will refine after first run
            rows = page.evaluate("""() => {
                const out = [];
                // Try table rows first
                document.querySelectorAll('table tbody tr, [class*="row"], [class*="position-item"]').forEach(tr => {
                    const cells = [...tr.querySelectorAll('td, [class*="cell"]')];
                    if (cells.length < 2) return;
                    const ticker = (cells[0]?.textContent || '').trim();
                    const name   = (cells[1]?.textContent || '').trim();
                    // Look for bull/bear signal anywhere in the row
                    const txt    = tr.textContent || '';
                    const signal = txt.match(/\\b(Bullish|Bearish|Bull|Bear|Long|Short|Neutral)\\b/i)?.[1] || '';
                    const trend  = txt.match(/\\b(Buy|Sell|Hold|Add|Reduce)\\b/i)?.[1] || '';
                    if (ticker && signal) out.push({ ticker, name, signal, trend });
                });
                return out;
            }""")

            log.info(f"Extracted {len(rows)} positions")
            for r in rows:
                sig = (r.get('signal') or '').lower()
                target = data['bullish'] if ('bull' in sig or 'long' in sig) else \
                         data['bearish'] if ('bear' in sig or 'short' in sig) else None
                if target is not None:
                    target.append({
                        'ticker': r.get('ticker', ''),
                        'name':   r.get('name', ''),
                        'signal': r.get('signal', ''),
                        'trend':  r.get('trend', '')
                    })

            # ── MACRO SHOW ───────────────────────────────────────────────────
            log.info("Scraping Macro Show...")
            # category_id for Macro Show varies; try common ones
            for macro_url in [
                'https://app.hedgeye.com/research_items?with_category_ids[]=8',
                'https://app.hedgeye.com/research_items?with_category_ids[]=1',
                'https://app.hedgeye.com/insights?tag=macro-show',
                'https://app.hedgeye.com/research_items?tag=macro-show',
            ]:
                page.goto(macro_url, wait_until='networkidle', timeout=20000)
                page.wait_for_timeout(2000)
                if 'not found' not in page.title().lower():
                    page.screenshot(path=os.path.join(DBG, '04_macro.png'))
                    with open(os.path.join(DBG, 'macro.html'), 'w', encoding='utf-8') as fh:
                        fh.write(page.content())
                    break

            macro = page.evaluate("""() => {
                // First article/card on the page
                const article = document.querySelector('article, [class*="research-item"], [class*="insight-card"], [class*="post"]');
                if (!article) return null;
                const title   = article.querySelector('h1,h2,h3,[class*="title"]')?.textContent?.trim() || '';
                const date    = article.querySelector('time,[class*="date"],[class*="published"]')?.textContent?.trim() || '';
                const bullets = [...article.querySelectorAll('li,p')]
                    .map(el => el.textContent.trim())
                    .filter(t => t.length > 20 && t.length < 400)
                    .slice(0, 10);
                return { title, date, bullets };
            }""")

            if macro:
                data['macro_show'] = macro

            browser.close()
            log.info(f"Scrape complete. Bull: {len(data['bullish'])}, Bear: {len(data['bearish'])}")
        finally:
            pw.stop()

    except Exception as e:
        log.error(f"Scrape error: {e}", exc_info=True)
        data['error'] = str(e)

    save_data(data)
    return data

# ── API routes ───────────────────────────────────────────────────────────────

@app.route('/api/data')
def api_data():
    d = load_data()
    if d:
        return jsonify(d)
    return jsonify({'error': 'No data yet — click Actualizar', 'bullish': [], 'bearish': [], 'macro_show': {}, 'updated': None})

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    d = scrape_hedgeye()
    return jsonify({'ok': True, 'updated': d.get('updated'),
                    'bullish': len(d.get('bullish', [])),
                    'bearish': len(d.get('bearish', [])),
                    'error': d.get('error')})

_NAMES_RE = r'Keith|McCullough'
# timestamps al final: "(4:02)", "(14:55, 22:20)"
_TS_RE = re.compile(r'\s*\(\d+:\d+(?:[,\s]+\d+:\d+)*\)\s*$')
# mid-sentence: ", y dijo/agregó/señaló que"
_MID_ATTR = re.compile(
    r',?\s+y\s+(dijo|agregó|añadió|señaló|reiteró|aclaró|explicó|describió|destacó)\s+(que\s+)?',
    re.IGNORECASE
)
# ", diciendo que X"
_DICIENDO = re.compile(r',?\s+diciendo\s+que\s+', re.IGNORECASE)
# "según él/McCullough/Keith,"
_SEGUN = re.compile(r',?\s*según\s+(él|ella|Keith|McCullough)\b[,]?\s*', re.IGNORECASE)
# 'reiteró: "cita"' → cita
_REITERO_CITA = re.compile(r'\w+:\s*[«"\'](.*?)[»"\']', re.IGNORECASE)

_VERBS_IMPL = (
    r'Dijo|Señaló|Reiteró|Agregó|Explicó|Destacó|Enfatizó|Añadió|Mencionó|'
    r'Citó|Afirmó|Indicó|Advirtió|Apuntó|Comentó|Subrayó|Reforzó|Recordó|'
    r'Reconoció|Rechazó|Insistió|Precisó|Sostuvo|Hizo'
)

def _limpiar_atribucion(texto):
    """Quita la cláusula de atribución al inicio del bullet."""
    # "Keith dijo/señaló/... que X" → X
    m = re.match(rf'({_NAMES_RE})\s+\S+\s+que\s+', texto, re.IGNORECASE)
    if m:
        resto = texto[m.end():]
        return (resto[0].upper() + resto[1:]) if resto else ''
    # "Keith abrió con petróleo, X" → X
    m2 = re.match(rf'({_NAMES_RE})\s+\S+(?:\s+con)?\s+[^,]+,\s*', texto, re.IGNORECASE)
    if m2:
        resto = texto[m2.end():]
        return (resto[0].upper() + resto[1:]) if resto else ''
    # "Dijo/Señaló/... que X" (sujeto implícito) → X
    m3 = re.match(rf'({_VERBS_IMPL})\s+que\s+', texto, re.IGNORECASE)
    if m3:
        resto = texto[m3.end():]
        return (resto[0].upper() + resto[1:]) if resto else ''
    # "Hizo hincapié en que X" → X
    m4 = re.match(r'Hizo\s+hincapi[eé]\s+en\s+que\s+', texto, re.IGNORECASE)
    if m4:
        resto = texto[m4.end():]
        return (resto[0].upper() + resto[1:]) if resto else ''
    return texto

def _limpiar_inline(texto):
    """Limpia atribuciones que aparecen en el medio de la oración."""
    t = _MID_ATTR.sub('. ', texto)
    t = _DICIENDO.sub('. ', t)
    t = _SEGUN.sub(' ', t)
    # "pero destacó/señaló/dijo que X" → ". X"
    t = re.sub(
        r',?\s+pero\s+(' + _VERBS_IMPL + r')\s+que\s+',
        '. ', t, flags=re.IGNORECASE
    )
    # "y reiteró/dijo: «cita»" → ". cita"  (verbo + colon antes de cita)
    t = re.sub(
        rf'\s+y\s+({_VERBS_IMPL}):\s*[«"\']?(.*?)[»"\']?(?=\.|,|$)',
        r'. \2', t, flags=re.IGNORECASE
    )
    # ' y «cita»' o ' y "cita"' — quitar conector antes de cita suelta
    t = re.sub(r'\s+y\s+[«"](.*?)[»"]', r'. \1', t)
    # 'X reiteró/dijo: «cita»' → contenido de la cita
    t = _REITERO_CITA.sub(lambda m: m.group(1), t)
    # "y que [cláusula]" mid-sentence (artefacto de "dijo que A y que B") → "y [cláusula]"
    t = re.sub(r'\s+y\s+que\s+', ' y ', t)
    # Dobles puntos ".. " → ". "
    t = re.sub(r'\.\s*\.\s*', '. ', t)
    return t

def _limpiar_gerundio(texto):
    """'Enfatizando que X' → X"""
    m = re.match(r'[A-ZÁÉÍÓÚÑ]\w+(?:ando|iendo)\s+que\s+', texto, re.IGNORECASE)
    if m:
        resto = texto[m.end():]
        return (resto[0].upper() + resto[1:]) if resto else texto
    return texto

def _primera_oracion(texto, max_chars=400):
    """Primera oración completa, máximo max_chars caracteres."""
    for sep in ('. ', '.\n'):
        idx = texto.find(sep)
        if 0 < idx <= max_chars:
            return texto[:idx + 1].strip()
    # Oración muy larga: cortar en colon si separa premisa de lista
    colon_idx = texto.find(': ')
    if 60 < colon_idx < max_chars:
        return texto[:colon_idx] + '.'
    # Último recurso: punto más cercano antes de max_chars
    trunc = texto[:max_chars]
    last_dot = trunc.rfind('.')
    if last_dot > 60:
        return texto[:last_dot + 1].strip()
    return trunc.rstrip(' ,;') + '…'

def _resumir_seccion(puntos):
    """Dos oraciones por sección, sin atribuciones."""
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

@app.route('/api/summarize', methods=['POST'])
def api_summarize():
    d = load_data()
    if not d:
        return jsonify({'error': 'Sin datos — actualizá primero'}), 400
    secciones = d.get('macro_show', {}).get('secciones', [])
    if not secciones:
        return jsonify({'error': 'Sin secciones para resumir'}), 400
    resumidas = [
        {'titulo': sec['titulo'], 'resumen': _resumir_seccion(sec.get('puntos', []))}
        for sec in secciones if sec.get('puntos')
    ]
    macro = d.get('macro_show', {})
    return jsonify({'ok': True, 'secciones': resumidas,
                    'macro_title':   macro.get('title', ''),
                    'macro_date':    macro.get('date', ''),
                    'updated':       d.get('updated', ''),
                    'bullish':       d.get('bullish', []),
                    'bearish':       d.get('bearish', []),
                    'macro_bullish': macro.get('bullish', []),
                    'macro_bearish': macro.get('bearish', [])})

@app.route('/api/status')
def api_status():
    d = load_data()
    return jsonify({'running': True,
                    'last_update': d.get('updated') if d else None,
                    'has_data': bool(d and (d.get('bullish') or d.get('bearish') or d.get('macro_show', {}).get('title')))})

# ── main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone='America/Argentina/Buenos_Aires')
    scheduler.add_job(scrape_hedgeye, 'cron', hour=17, minute=0)
    scheduler.start()
    log.info("Hedgeye server running at http://localhost:5050")
    log.info("Auto-scrape scheduled daily at 17:00 ART")
    app.run(host='127.0.0.1', port=5050, debug=False, use_reloader=False)
