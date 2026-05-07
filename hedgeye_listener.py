"""
Hedgeye Listener — escucha ntfy.sh y ejecuta el scraper cuando recibe un trigger.
Para iniciar: python hedgeye_listener.py
Mantene esta ventana abierta mientras uses el CRM desde otra PC.
"""
import json, os, re, subprocess, sys, datetime, time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)
    import requests

TOPIC = 'crm-hg-dsalem123-offshore'
BASE  = os.path.dirname(os.path.abspath(__file__))

def ts():
    return datetime.datetime.now().strftime('%H:%M:%S')

def run_scraper():
    print(f'[{ts()}] Ejecutando scraper de Hedgeye...')
    scraper = os.path.join(BASE, 'hedgeye_scraper.py')
    result  = subprocess.run([sys.executable, scraper], timeout=300)
    if result.returncode == 0:
        print(f'[{ts()}] Scraper OK')
        return True
    print(f'[{ts()}] Scraper fallo con codigo {result.returncode}')
    return False

def update_html():
    data_file = os.path.join(BASE, 'hedgeye_data.json')
    if not os.path.exists(data_file):
        print('No hay hedgeye_data.json — abortando')
        return False
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data_json = json.dumps(data, ensure_ascii=False)
    new_line  = f'const HG_STATIC_DATA = {data_json};'
    for fname in ['crm_offshore_cambios.html', 'index.html']:
        path = os.path.join(BASE, fname)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = re.sub(
            r'const HG_STATIC_DATA = (?:null|\{[\s\S]*?\});',
            new_line,
            content,
            count=1
        )
        if new_content == content:
            print(f'  AVISO: no se encontro HG_STATIC_DATA en {fname}')
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'[{ts()}] {fname} actualizado con datos nuevos')
    return True

def git_push():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    os.chdir(BASE)
    subprocess.run(['git', 'add', 'crm_offshore_cambios.html', 'index.html'])
    result_commit = subprocess.run(
        ['git', 'commit', '-m', f'Hedgeye update {now}'],
        capture_output=True, text=True
    )
    if 'nothing to commit' in result_commit.stdout:
        print(f'[{ts()}] Sin cambios para commitear')
        return
    result_push = subprocess.run(['git', 'push'])
    if result_push.returncode == 0:
        print(f'[{ts()}] Push OK — Vercel actualiza en ~30 segundos')
    else:
        print(f'[{ts()}] Error en git push')

def handle_trigger():
    ok = run_scraper()
    if ok and update_html():
        git_push()
    else:
        print(f'[{ts()}] No se pudo completar la actualizacion')

def listen():
    print('=' * 55)
    print('  Hedgeye Listener — CRM ExpressLine')
    print(f'  Topic: ntfy.sh/{TOPIC}')
    print('  Esperando triggers desde Vercel...')
    print('  Mantene esta ventana abierta.')
    print('=' * 55)
    url = f'https://ntfy.sh/{TOPIC}/json'
    while True:
        try:
            with requests.get(url, stream=True, timeout=None) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            msg = json.loads(line)
                            if msg.get('event') == 'message':
                                print(f'\n[{ts()}] Trigger recibido desde Vercel!')
                                handle_trigger()
                                print(f'\nEsperando proximo trigger...')
                        except Exception as e:
                            print(f'Error procesando mensaje: {e}')
        except Exception as e:
            print(f'[{ts()}] Conexion perdida ({e}) — reconectando en 5s...')
            time.sleep(5)

if __name__ == '__main__':
    listen()
