"""
Hedgeye scraper usando undetected-chromedriver (bypasea Cloudflare)
"""
import json, os, sys, datetime, time, re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Traducción fallback (Google Translate) ────────────────────────────────────
try:
    from deep_translator import GoogleTranslator
    _gt = GoogleTranslator(source='en', target='es')
    def _traducir_google(txt):
        if not txt or not txt.strip(): return txt
        try: return _gt.translate(txt)
        except: return txt
except ImportError:
    def _traducir_google(txt): return txt

# ── Procesamiento con Claude (traducción + resúmenes + executive summary) ─────
def procesar_con_claude(titulo, secciones_raw, bull_tickers, bear_tickers, api_key):
    """
    Un solo call a Claude que:
    1. Traduce al español con jerga financiera profesional
    2. Elimina atribuciones ("Keith dijo que...") — comienza directo con el punto
    3. Genera resumen de 1-2 oraciones por sección
    4. Genera executive summary estructurado

    Returns: (titulo_es, secciones_es, resumen_ejecutivo) o (None, None, None) si falla.
    """
    try:
        import anthropic, json as _j
        client = anthropic.Anthropic(api_key=api_key)

        payload = {
            "titulo": titulo,
            "secciones": [{"titulo": s["titulo"], "puntos": s["puntos"]} for s in secciones_raw],
            "bull_tickers": bull_tickers[:15],
            "bear_tickers": bear_tickers[:15],
        }

        prompt = (
            "Sos un chief macro strategist de una firma institucional de wealth management. "
            "Procesá el siguiente contenido del Macro Show de Hedgeye y respondé ÚNICAMENTE con JSON válido.\n\n"
            "TAREAS:\n"
            "1. Traducí al español profesional institucional\n"
            "2. Eliminá TODA atribución de sujeto: 'Keith dijo que X' → 'X'; 'Señaló que Y' → 'Y'; 'McCullough destacó Z' → 'Z'\n"
            "3. Títulos de sección: 4-7 palabras, analíticos, en mayúsculas, sin sujeto\n"
            "4. Por cada sección generá un 'resumen' de 1-2 oraciones que sintetice los puntos clave con implicación práctica\n"
            "5. Generá un 'resumen_ejecutivo' macro del episodio completo\n\n"
            "TERMINOLOGÍA: usá jerga financiera profesional: corto/largo, rendimiento, tasa, rango de riesgo, señal de Tendencia/Comercio, "
            "impulso/momentum, sobreextendido, corrección, catalizador, posicionamiento, Quad 1/2/3/4. "
            "Preservá siempre: tickers (TLT, SPY, NVDA...), 'Quad N', números, ETFs.\n\n"
            "FORMATO (JSON estricto, sin markdown, sin texto extra):\n"
            '{"titulo":"...","secciones":[{"titulo":"...","puntos":["..."],"resumen":"1-2 oraciones"}],'
            '"resumen_ejecutivo":{"tesis":"mensaje macro central 1-2 oraciones",'
            '"contexto":"condiciones de mercado actuales 1 oración",'
            '"insights":["insight accionable 1","insight accionable 2","insight accionable 3"],'
            '"conclusion":"implicación concreta para gestión de portfolios 1 oración"}}\n\n'
            "CONTENIDO:\n" + _j.dumps(payload, ensure_ascii=False)
        )

        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=6000,
            messages=[{'role': 'user', 'content': prompt}]
        )

        resp = msg.content[0].text.strip()
        if resp.startswith('```'):
            resp = re.sub(r'^```\w*\n?', '', resp)
            resp = re.sub(r'\n?```$', '', resp.strip())

        result = _j.loads(resp)

        titulo_es = result.get('titulo', titulo)
        secciones_es = []
        for i, sec in enumerate(result.get('secciones', [])):
            orig = secciones_raw[i] if i < len(secciones_raw) else {}
            secciones_es.append({
                'titulo':  sec.get('titulo',  orig.get('titulo', '')),
                'puntos':  sec.get('puntos',  orig.get('puntos', [])),
                'resumen': sec.get('resumen', ''),
            })

        resumen_ejecutivo = result.get('resumen_ejecutivo', None)
        print(f"  Claude: {len(secciones_es)} secciones, exec summary OK", flush=True)
        return titulo_es, secciones_es, resumen_ejecutivo

    except Exception as e:
        print(f"  Claude procesamiento error: {e}", flush=True)
        return None, None, None

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
CFG  = os.path.join(BASE, 'hedgeye_config.json')
DATA = os.path.join(BASE, 'hedgeye_data.json')
RAW  = os.path.join(BASE, 'hedgeye_raw.json')   # data cruda en inglés para AI posterior
DBG  = os.path.join(BASE, 'hedgeye_debug')
os.makedirs(DBG, exist_ok=True)

with open(CFG, encoding='utf-8') as f:
    cfg = json.load(f)

data = {
    "updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    "bullish": [], "bearish": [],
    "macro_show": {"title": "", "date": "", "bullets": [], "bullish": [], "bearish": [], "es_replay": False},
    "error": None
}

def save():
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def dbg(name, html):
    with open(os.path.join(DBG, name), 'w', encoding='utf-8') as f:
        f.write(html)

CF_MARKERS = ['un momento', 'just a moment', 'verificaci', 'momento...', 'moment...', 'checking your']

def is_cf_page(driver):
    return any(s in driver.title.lower() for s in CF_MARKERS)

def check_session(driver, cookies_file):
    """Si fue redirigido al login, borra cookies y lanza excepción."""
    if 'sign_in' in driver.current_url or 'accounts.hedgeye.com' in driver.current_url:
        print(f"  Sesión expirada mid-scrape (URL: {driver.current_url})", flush=True)
        if os.path.exists(cookies_file):
            os.remove(cookies_file)
            print("  Cookies borradas — próximo scrape hará login completo", flush=True)
        raise Exception("Sesión expirada durante el scraping — cookies borradas, reintentar")

def wait_for_page(driver, timeout=90):
    """Espera que Cloudflare resuelva el challenge."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_cf_page(driver):
            return True
        print(f"  CF challenge: '{driver.title}' - esperando...", flush=True)
        time.sleep(3)
    print(f"  WARN: CF no resolvio en {timeout}s. Title: '{driver.title}'", flush=True)
    return False

def parse_positions(html):
    """Parsea long/short positions de la pagina open_signals."""
    soup = BeautifulSoup(html, 'html.parser')
    bull, bear = [], []

    for table in soup.select('table.performance, table.sortable-list'):
        header = table.select_one('thead th.heading')
        if not header:
            continue
        h_text = header.get_text(separator=' ', strip=True).lower()
        is_long = 'long' in h_text
        is_short = 'short' in h_text

        for row in table.select('tr.position'):
            # Ticker en td.symbol o td.se-position-symbol
            sym = row.select_one('td.symbol, .se-position-symbol')
            if not sym:
                continue
            ticker = sym.get_text(strip=True)
            if not ticker or len(ticker) > 8:
                continue

            # Nombre de empresa desde alt de logo
            img = row.select_one('img.se-logo')
            name = img.get('alt', '').replace(' Logo', '').strip() if img else ''

            # Fallback: detectar por clase orb si el header no fue claro
            row_is_long = is_long
            row_is_short = is_short
            if not row_is_long and not row_is_short:
                orb = row.select_one('li.orb')
                if orb:
                    classes = orb.get('class', [])
                    row_is_long = 'long' in classes
                    row_is_short = 'short' in classes

            if row_is_long:
                item = {'ticker': ticker, 'name': name, 'signal': 'Bullish', 'trend': 'Long'}
                if not any(x['ticker'] == ticker for x in bull):
                    bull.append(item)
            elif row_is_short:
                item = {'ticker': ticker, 'name': name, 'signal': 'Bearish', 'trend': 'Short'}
                if not any(x['ticker'] == ticker for x in bear):
                    bear.append(item)

    return bull, bear

def parse_macro_sections(html):
    """Extrae secciones del articulo Macro Show.
    Soporta tres formatos:
      - Keith: h6 + ul/li
      - Ryan/otros: h3.text-black + parrafos p con bullet •
      - AI Summary: h3 MAIN SUMMARY + <p><strong>Titulo</strong>• bullet...</p>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select_one('#content') or soup
    sections = []
    TS_RE = re.compile(r'\s*\(\d+:\d+[–\-]\d+:\d+(?:,\s*\d+:\d+[–\-]\d+:\d+)*\)\s*$')
    SKIP_TEXT = ['reflect commentary', 'access today', 'CLICK HERE', 'enhanced by AI',
                 'may contain errors', 'access the macro', 'watch on-demand']

    def _clean(t):
        t = TS_RE.sub('', t).strip()
        t = re.sub(r'\s{2,}', ' ', t).strip()
        return t

    def _ok_bullet(t):
        tl = t.lower()
        if re.match(r'^[,;]\s', t):  # fragmento: continuación de link recortado
            return False
        return 30 < len(t) < 700 and not any(s in tl for s in SKIP_TEXT)

    # ── Formato AI Summary (MAIN SUMMARY h3 + p>strong) ──────────────────────
    main_h3 = None
    for h3 in content.find_all('h3'):
        if 'MAIN SUMMARY' in h3.get_text():
            main_h3 = h3
            break

    if main_h3:
        cur_title, cur_pts = None, []
        STOP = ['Summary has been', 'enhanced by AI']
        for el in main_h3.find_next_siblings():
            if el.name in ('h3', 'h4') and any(s in el.get_text() for s in STOP):
                break
            if el.name != 'p':
                continue
            strong = el.find('strong')
            full_text = el.get_text(separator='•', strip=True)
            if strong:
                strong_txt = strong.get_text(strip=True)
                # Guardar sección previa
                if cur_title and cur_pts:
                    sections.append({'titulo': cur_title, 'puntos': cur_pts})
                cur_title = strong_txt
                cur_pts = []
                # Bullets mezclados en el mismo <p> después del título
                remainder = full_text[len(strong_txt):].strip().lstrip('•').strip()
                if remainder:
                    for chunk in remainder.split('•'):
                        pt = _clean(chunk)
                        if _ok_bullet(pt):
                            cur_pts.append(pt)
            elif full_text.strip():
                # <p> sin strong: puede ser bullet(s) o título sin negrita
                raw = full_text.strip()
                if raw.startswith('•') or (cur_title and not any(raw.startswith(s) for s in ['CLICK', 'The summary'])):
                    for chunk in raw.split('•'):
                        pt = _clean(chunk)
                        if _ok_bullet(pt):
                            cur_pts.append(pt)
        if cur_title and cur_pts:
            sections.append({'titulo': cur_title, 'puntos': cur_pts})
        if sections:
            return sections

    # ── Formatos clásicos: h6+ul o h3+p ──────────────────────────────────────
    cur_title, cur_pts = None, []
    SKIP_H3 = ['TL;DR', 'Summary has been', 'Access The Macro', 'MAIN SUMMARY', 'Market and Macro']

    for el in content.find_all(['h3', 'h6', 'ul', 'p']):
        tag = el.name
        text = el.get_text(separator=' ', strip=True)

        if tag in ('h3', 'h6'):
            if cur_title and cur_pts:
                sections.append({'titulo': cur_title, 'puntos': cur_pts})
            if tag == 'h3' and (any(s in text for s in SKIP_H3) or len(text) < 5):
                cur_title = None; cur_pts = []
            else:
                cur_title = text; cur_pts = []

        elif tag == 'ul' and cur_title:
            for li in el.select('li'):
                pt = _clean(li.get_text(separator=' ', strip=True))
                if _ok_bullet(pt):
                    cur_pts.append(pt)

        elif tag == 'p' and cur_title:
            if el.parent and el.parent.name in ('li', 'ul'):
                continue
            pt = _clean(re.sub(r'^[•·\-]\s*', '', text))
            if _ok_bullet(pt):
                cur_pts.append(pt)

    if cur_title and cur_pts:
        sections.append({'titulo': cur_title, 'puntos': cur_pts})
    return sections

def parse_macro_tldr(html):
    """Extrae posiciones BULLISH/BEARISH del TL;DR del Macro Show."""
    soup = BeautifulSoup(html, 'html.parser')
    bull_tickers, bear_tickers = [], []

    # Buscar parrafos con BULLISH / BEARISH
    for p in soup.select('p, li'):
        txt = p.get_text(separator=' ', strip=True)
        # Linea BULLISH: "• BULLISH: BNO; NORW; ..."
        if re.search(r'BULLISH\s*:', txt, re.I):
            # Extraer parte despues de BULLISH:
            m = re.search(r'BULLISH\s*:\s*(.+)', txt, re.I)
            if m:
                raw = m.group(1)
                # Extraer tickers (en parentesis o palabras en mayusculas 2-5 chars)
                tickers = re.findall(r'\(([A-Z]{1,6})\)', raw)
                if not tickers:
                    tickers = re.findall(r'\b([A-Z]{2,6})\b', raw)
                bull_tickers = [t for t in tickers if t not in ('THE', 'AND', 'FOR', 'NOT', 'BUT')]
        elif re.search(r'BEARISH\s*:', txt, re.I):
            m = re.search(r'BEARISH\s*:\s*(.+)', txt, re.I)
            if m:
                raw = m.group(1)
                tickers = re.findall(r'\(([A-Z]{1,6})\)', raw)
                if not tickers:
                    tickers = re.findall(r'\b([A-Z]{2,6})\b', raw)
                bear_tickers = [t for t in tickers if t not in ('THE', 'AND', 'FOR', 'NOT', 'BUT')]

    return bull_tickers, bear_tickers

def _detect_chrome_version():
    """Devuelve el major version de Chrome instalado (int) o None si no se puede detectar."""
    import subprocess, re, winreg
    # 1. Registry (más rápido y confiable en Windows)
    for hive, path in [
        (winreg.HKEY_CURRENT_USER,  r'Software\Google\Chrome\BLBeacon'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Google\Chrome\BLBeacon'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Google\Chrome\BLBeacon'),
    ]:
        try:
            key = winreg.OpenKey(hive, path)
            ver = winreg.QueryValueEx(key, 'version')[0]
            return int(ver.split('.')[0])
        except Exception:
            pass
    # 2. Ejecutable directo
    for exe in [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    ]:
        if os.path.exists(exe):
            try:
                r = subprocess.run([exe, '--version'], capture_output=True, text=True, timeout=5)
                m = re.search(r'(\d+)\.', r.stdout)
                if m:
                    return int(m.group(1))
            except Exception:
                pass
    return None

driver = None
try:
    chrome_ver = _detect_chrome_version()
    print(f"Iniciando Chrome (undetected, version={chrome_ver})...", flush=True)
    COOKIES_FILE = os.path.join(BASE, 'hedgeye_cookies.json')
    has_cookies = os.path.exists(COOKIES_FILE)

    options = uc.ChromeOptions()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    # Siempre non-headless: headless falla en Windows Y Cloudflare Turnstile lo detecta
    driver = uc.Chrome(options=options, headless=False, version_main=chrome_ver)

    # Deshabilitar window.print() para evitar dialogos de impresion
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'window.print = function(){};'
    })

    print(f"Modo: {'con cookies (minimizado)' if has_cookies else 'visible (primer login)'}", flush=True)
    wait = WebDriverWait(driver, 25)

    # ── LOGIN ────────────────────────────────────────────────────────────────
    MACRO_URL = 'https://app.hedgeye.com/feed_items/all?page=1&with_category=43-the-macro-show'

    if has_cookies:
        print("Cargando cookies guardadas...", flush=True)
        driver.get('https://app.hedgeye.com')
        wait_for_page(driver, 30)
        time.sleep(2)
        with open(COOKIES_FILE) as f:
            for cookie in json.load(f):
                try: driver.add_cookie(cookie)
                except: pass
        driver.get(MACRO_URL)
        wait_for_page(driver, 30)
        time.sleep(3)
        if 'sign_in' in driver.current_url or 'accounts.hedgeye.com' in driver.current_url:
            print("Cookies expiradas - haciendo login completo", flush=True)
            has_cookies = False
            os.remove(COOKIES_FILE)
        else:
            print(f"Login via cookies OK — en The Macro Show: {driver.current_url}", flush=True)
            try: driver.minimize_window()
            except: pass

    logged_in = has_cookies

    if not logged_in:
        print("Navegando al login...", flush=True)
        driver.get('https://accounts.hedgeye.com/users/sign_in')
        wait_for_page(driver, 60)
        time.sleep(3)
        dbg('01_login.html', driver.page_source)
        print(f"Login URL: {driver.current_url}", flush=True)

        from selenium.webdriver.common.keys import Keys

        # Usar send_keys real (no execute_script) para disparar eventos DOM del form
        email_sel = '#user_email, input[name="user[email]"], input[type="email"]'
        email = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, email_sel)))
        email.click(); time.sleep(0.3)
        email.clear(); time.sleep(0.2)
        email.send_keys(cfg['email']); time.sleep(0.3)
        print(f"Email llenado: {cfg['email'][:20]}...", flush=True)

        pwd_sel = '#user_password, input[name="user[password]"], input[type="password"]'
        pwd = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, pwd_sel)))
        pwd.click(); time.sleep(0.3)
        pwd.clear(); time.sleep(0.2)
        pwd.send_keys(cfg['password']); time.sleep(0.5)
        print("Password llenado", flush=True)

        dbg('01b_filled.html', driver.page_source)

        # Click submit por ID específico primero, fallback a otros selectores
        submitted = False
        for sel in ['#se-be-login-submit', 'input[name="commit"]', 'input[type="submit"]', 'button[type="submit"]']:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    print(f"Submit via: {sel}", flush=True)
                    submitted = True
                    break
            except: pass
        if not submitted:
            # Fallback: Enter en el campo de password
            pwd.send_keys(Keys.RETURN)
            print("Submit via Keys.RETURN", flush=True)

        # Esperar Cloudflare challenge si aparece, luego dar tiempo al login
        time.sleep(3)
        wait_for_page(driver, 90)
        time.sleep(10)
        print(f"Post-login URL: {driver.current_url}", flush=True)
        dbg('02_after_login.html', driver.page_source)

        # Verificar si el login falló (redirigió de vuelta a sign_in o a accounts)
        cur = driver.current_url
        if 'sign_in' in cur or ('accounts.hedgeye.com' in cur and 'app.hedgeye.com' not in cur):
            # Borrar cookies corruptas para que el próximo intento haga login limpio
            if os.path.exists(COOKIES_FILE):
                os.remove(COOKIES_FILE)
                print("Cookies borradas — próximo scrape reintentará login", flush=True)
            data['error'] = f'Login failed (URL: {cur}) - verificar credenciales en hedgeye_config.json'
            driver.quit(); save(); sys.exit(1)

        with open(COOKIES_FILE, 'w') as f:
            json.dump(driver.get_cookies(), f)
        print("Cookies guardadas", flush=True)
        try: driver.minimize_window()
        except: pass

    # ── OPEN SIGNALS (Bullish / Bearish) ──────────────────────────────────────
    print("Scraping open signals...", flush=True)
    driver.get('https://app.hedgeye.com/stock_positions/open_signals')
    wait_for_page(driver, 90)
    time.sleep(6)
    check_session(driver, COOKIES_FILE)
    html = driver.page_source
    dbg('03_open_signals.html', html)
    print(f"Open signals title: '{driver.title}'", flush=True)
    bull, bear = parse_positions(html)
    data['bullish'] = bull
    data['bearish'] = bear
    print(f"Bull: {len(bull)}, Bear: {len(bear)}", flush=True)

    # ── MACRO SHOW ────────────────────────────────────────────────────────────
    print("Scraping Macro Show...", flush=True)
    driver.get('https://app.hedgeye.com/feed_items/all?page=1&with_category=43-the-macro-show')
    wait_for_page(driver, 90)
    time.sleep(6)
    check_session(driver, COOKIES_FILE)
    html = driver.page_source
    dbg('04_macro_list.html', html)
    soup_m = BeautifulSoup(html, 'html.parser')

    # Buscar primer link a articulo (/feed_items/NNN)
    first_link = None
    for a in soup_m.select('a[href]'):
        href = a.get('href', '')
        if re.search(r'/feed_items/\d+', href):
            # Usar version /print para HTML limpio
            base_href = href.rstrip('/')
            if not base_href.endswith('/print'):
                base_href = base_href + '/print'
            first_link = base_href if base_href.startswith('http') else 'https://app.hedgeye.com' + base_href
            break
    if not first_link:
        for a in soup_m.select('a[href*="feed_items"]'):
            href = a.get('href', '')
            if href and '/feed_items/all' not in href and 'page=' not in href and 'category' not in href:
                base_href = href.rstrip('/')
                if not base_href.endswith('/print'):
                    base_href = base_href + '/print'
                first_link = base_href if base_href.startswith('http') else 'https://app.hedgeye.com' + base_href
                break

    if first_link:
        print(f"Abriendo Macro Show: {first_link}", flush=True)
        driver.get(first_link)
        wait_for_page(driver, 90)
        time.sleep(5)
        html_art = driver.page_source
        dbg('04_macro_article.html', html_art)
        soup_art = BeautifulSoup(html_art, 'html.parser')

        # Titulo y fecha
        te = soup_art.select_one('h1#headline, h1, h2')
        de = soup_art.select_one('.timestamp, time, .date, [class*="date"]')

        # Bullets principales (parrafos con contenido, sin duplicados)
        seen = set()
        bullets = []
        for el in soup_art.select('li > p, div#content > ul > li, div#content > p'):
            txt = el.get_text(strip=True)
            if (30 < len(txt) < 600
                    and 'BULLISH' not in txt and 'BEARISH' not in txt
                    and 'access' not in txt.lower()[:20]
                    and txt not in seen):
                seen.add(txt)
                bullets.append(txt)
            if len(bullets) >= 10:
                break

        # TL;DR: posiciones BULLISH/BEARISH del Macro Show
        macro_bull, macro_bear = parse_macro_tldr(html_art)

        print("Extrayendo secciones estructuradas...", flush=True)
        titulo = te.get_text(strip=True) if te else ''
        secciones_raw = parse_macro_sections(html_art)
        print(f"Secciones encontradas: {len(secciones_raw)}", flush=True)

        # Detectar episodio de replay / resumen (formato diferente al Macro Show regular)
        _REPLAY_KW = ['resumidas', 'repetición', 'replay', 'on-demand', 'recap', 'resumen del día']
        is_replay = any(kw in titulo.lower() for kw in _REPLAY_KW)
        if is_replay:
            print(f"INFO: Episodio de replay detectado: '{titulo}'", flush=True)

        # Detectar si el articulo solo tiene el livestream (notas no publicadas aun)
        content_div = soup_art.select_one('#content') or soup_art
        all_text = content_div.get_text(separator=' ', strip=True)
        is_livestream_only = (
            len(secciones_raw) == 0 or
            (len(secciones_raw) == 1 and any(
                kw in all_text for kw in ['jwplayer', 'Watch below', 'Míralo a continuación', 'submit questions', 'on-demand']
            ))
        )
        if is_livestream_only:
            print("WARN: Articulo solo tiene livestream, notas no publicadas aun.", flush=True)

        # ── Guardar raw (inglés) para procesamiento AI posterior con Claude Code ──
        raw_data = {
            "updated":    data["updated"],
            "bullish":    data["bullish"],
            "bearish":    data["bearish"],
            "macro_show": {
                "title":    titulo,
                "date":     de.get_text(strip=True) if de else '',
                "secciones": secciones_raw,
                "bullish":  macro_bull,
                "bearish":  macro_bear,
                "notas_pendientes": is_livestream_only,
                "es_replay": is_replay,
            }
        }
        with open(RAW, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"Raw data guardada -> hedgeye_raw.json ({len(secciones_raw)} secciones)", flush=True)

        # ── Procesamiento: Claude API primero, fallback Google Translate ──────────
        api_key = cfg.get('anthropic_api_key') or os.environ.get('ANTHROPIC_API_KEY', '')
        titulo_es, secciones_es, resumen_ejecutivo = None, None, None

        if api_key and not is_livestream_only and secciones_raw:
            print("Procesando con Claude (traducción + resúmenes + executive summary)...", flush=True)
            titulo_es, secciones_es, resumen_ejecutivo = procesar_con_claude(
                titulo, secciones_raw, macro_bull, macro_bear, api_key
            )

        if not secciones_es:
            print("Traduciendo con Google Translate (fallback)...", flush=True)
            titulo_es = _traducir_google(titulo)
            secciones_es = []
            for sec in secciones_raw:
                secciones_es.append({
                    'titulo':  _traducir_google(sec['titulo']),
                    'puntos':  [_traducir_google(p) for p in sec['puntos']],
                    'resumen': '',
                })

        data['macro_show'] = {
            'title':               titulo_es or titulo,
            'date':                de.get_text(strip=True) if de else '',
            'bullets':             [],
            'secciones':           secciones_es,
            'bullish':             macro_bull,
            'bearish':             macro_bear,
            'resumen_ai':          None,
            'resumen_ejecutivo':   resumen_ejecutivo,
            'notas_pendientes':    is_livestream_only,
            'es_replay':           is_replay,
        }
        print(f"Macro: '{data['macro_show']['title']}'", flush=True)
        print(f"Macro Bull tickers: {macro_bull}", flush=True)
        print(f"Macro Bear tickers: {macro_bear}", flush=True)
    else:
        print("No se encontro link al Macro Show article", flush=True)

    driver.quit()
    print(f"Listo. Bull: {len(data['bullish'])}, Bear: {len(data['bearish'])}", flush=True)

except Exception as e:
    import traceback
    print(f"ERROR: {e}\n{traceback.format_exc()}", flush=True)
    data['error'] = str(e)
    if driver:
        try: driver.quit()
        except: pass

save()
