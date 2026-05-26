"""
Hedgeye scraper usando undetected-chromedriver (bypasea Cloudflare)
"""
import json, os, sys, datetime, time, re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from deep_translator import GoogleTranslator
    _translator = GoogleTranslator(source='en', target='es')
    def traducir(txt):
        if not txt or not txt.strip(): return txt
        try: return _translator.translate(txt)
        except: return txt
except ImportError:
    def traducir(txt): return txt

def generar_resumen_ai(titulo, bullets, bull_tickers, bear_tickers, api_key):
    """Genera un resumen estructurado en español usando Claude API."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        contenido_raw = '\n'.join(f'- {b}' for b in bullets)
        bull_str = ', '.join(bull_tickers)
        bear_str = ', '.join(bear_tickers) if bear_tickers else 'ninguna'
        prompt = f"""Sos un analista financiero experto. Analizá el siguiente resumen del Macro Show de Hedgeye (Keith McCullough) y generá un resumen ejecutivo completo en español para un asesor de wealth management.

Episodio: {titulo}
Posiciones Bullish: {bull_str}
Posiciones Bearish: {bear_str}

Contenido del episodio:
{contenido_raw}

Generá un resumen ejecutivo estructurado con:
1. **Visión macro del mercado** (2-3 oraciones sobre el entorno macro actual según Keith)
2. **Tesis principal** (la idea central del episodio en 1-2 oraciones)
3. **Posiciones clave y por qué** (explica brevemente por qué está bull/bear en los activos principales)
4. **Señales de alerta** (riesgos o cambios que mencionó)
5. **Conclusión para el asesor** (qué implica esto para la cartera)

Usá un tono profesional y concreto. Máximo 400 palabras."""

        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=800,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        print(f"  AI summary error: {e}", flush=True)
        return None

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
CFG  = os.path.join(BASE, 'hedgeye_config.json')
DATA = os.path.join(BASE, 'hedgeye_data.json')
DBG  = os.path.join(BASE, 'hedgeye_debug')
os.makedirs(DBG, exist_ok=True)

with open(CFG, encoding='utf-8') as f:
    cfg = json.load(f)

data = {
    "updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    "bullish": [], "bearish": [],
    "macro_show": {"title": "", "date": "", "bullets": [], "bullish": [], "bearish": []},
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
    Soporta dos formatos:
      - Keith: h6 + ul/li
      - Ryan/otros: h3.text-black + parrafos p con bullet punto
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.select_one('#content') or soup
    sections = []
    cur_title, cur_pts = None, []

    SKIP_H3 = ['TL;DR', 'Summary has been', 'Access The Macro', 'MAIN SUMMARY', 'Market and Macro']
    TS_RE = re.compile(r'\s*\(\d+:\d+[–\-]\d+:\d+(?:,\s*\d+:\d+[–\-]\d+:\d+)*\)\s*$')

    for el in content.find_all(['h3', 'h6', 'ul', 'p']):
        tag = el.name
        text = el.get_text(separator=' ', strip=True)

        if tag in ('h3', 'h6'):
            if cur_title and cur_pts:
                sections.append({'titulo': cur_title, 'puntos': cur_pts})
            if tag == 'h3' and (any(s in text for s in SKIP_H3) or len(text) < 5):
                cur_title = None
                cur_pts = []
            else:
                cur_title = text
                cur_pts = []

        elif tag == 'ul' and cur_title:
            # Formato Keith: ul > li
            for li in el.select('li'):
                pt = li.get_text(separator=' ', strip=True)
                pt = TS_RE.sub('', pt).strip()
                if 30 < len(pt) < 700:
                    cur_pts.append(pt)

        elif tag == 'p' and cur_title:
            # Saltar <p> anidados dentro de <li> — ya procesados por el handler de ul
            if el.parent and el.parent.name in ('li', 'ul'):
                continue
            # Formato Ryan: parrafos sueltos con bullet •
            pt = re.sub(r'^[•·\-]\s*', '', text).strip()
            pt = TS_RE.sub('', pt).strip()
            if (30 < len(pt) < 700
                    and 'reflect commentary' not in pt.lower()
                    and 'access today' not in pt.lower()
                    and 'CLICK HERE' not in pt):
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

driver = None
try:
    print("Iniciando Chrome (undetected)...", flush=True)
    COOKIES_FILE = os.path.join(BASE, 'hedgeye_cookies.json')
    has_cookies = os.path.exists(COOKIES_FILE)

    options = uc.ChromeOptions()
    options.add_argument('--window-size=1280,800')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    # Siempre non-headless: headless falla en Windows Y Cloudflare Turnstile lo detecta
    driver = uc.Chrome(options=options, headless=False, version_main=148)

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
        time.sleep(4)
        dbg('01_login.html', driver.page_source)
        print(f"Login URL: {driver.current_url}", flush=True)

        from selenium.webdriver.common.keys import Keys
        email_sel = '#user_email, input[name="user[email]"], input[type="email"]'
        email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, email_sel)))
        driver.execute_script("arguments[0].value = arguments[1];", email, cfg['email'])
        email.click(); email.send_keys(Keys.END); time.sleep(0.3)
        print("Email llenado", flush=True)

        pwd_sel = '#user_password, input[name="user[password]"], input[type="password"]'
        pwd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, pwd_sel)))
        driver.execute_script("arguments[0].value = arguments[1];", pwd, cfg['password'])
        pwd.click(); pwd.send_keys(Keys.END); time.sleep(0.5)
        print("Password llenado", flush=True)

        for sel in ['input[name="commit"]', 'input[type="submit"]', 'button[type="submit"]', 'button']:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel)
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"Submit via: {sel}", flush=True); break
            except: pass

        time.sleep(6)
        print(f"Post-login URL: {driver.current_url}", flush=True)

        if 'sign_in' in driver.current_url:
            data['error'] = 'Login failed - verificar credenciales en hedgeye_config.json'
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

        print("Traduciendo contenido al espanol...", flush=True)
        secciones_es = []
        for sec in secciones_raw:
            titulo_sec = traducir(sec['titulo'])
            puntos_es  = [traducir(p) for p in sec['puntos']]
            secciones_es.append({'titulo': titulo_sec, 'puntos': puntos_es})

        data['macro_show'] = {
            'title':          traducir(titulo),
            'date':           de.get_text(strip=True) if de else '',
            'bullets':        [],
            'secciones':      secciones_es,
            'bullish':        macro_bull,
            'bearish':        macro_bear,
            'resumen_ai':     None,
            'notas_pendientes': is_livestream_only,
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
