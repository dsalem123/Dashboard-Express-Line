"""
Llama a Claude Code CLI para procesar hedgeye_raw.json -> hedgeye_data.json
con traducción institucional + resumen ejecutivo.
Invocado automáticamente por handle_hedgeye_trigger() en hedgeye_listener.py.
"""
import subprocess, sys, os, json, datetime

BASE   = os.path.dirname(os.path.abspath(__file__))
RAW    = os.path.join(BASE, 'hedgeye_raw.json')
DATA   = os.path.join(BASE, 'hedgeye_data.json')
CLAUDE = r'C:\Users\usuario\.local\bin\claude.exe'

def ts():
    return datetime.datetime.now().strftime('%H:%M:%S')

# ── Validaciones ──────────────────────────────────────────────────────────────
if not os.path.exists(RAW):
    print(f'[{ts()}] ai_process: hedgeye_raw.json no encontrado'); sys.exit(1)

if not os.path.exists(CLAUDE):
    print(f'[{ts()}] ai_process: claude.exe no encontrado'); sys.exit(1)

with open(RAW, encoding='utf-8') as f:
    raw = json.load(f)

if raw.get('macro_show', {}).get('notas_pendientes'):
    print(f'[{ts()}] ai_process: notas no publicadas, saltando'); sys.exit(0)

if not raw.get('macro_show', {}).get('secciones'):
    print(f'[{ts()}] ai_process: sin secciones, saltando'); sys.exit(0)

# ── Prompt corto — instrucciones completas están en _ai_instrucciones.md ─────
prompt = (
    f'Leé el archivo _ai_instrucciones.md para las instrucciones completas de procesamiento. '
    f'Luego leé hedgeye_raw.json, procesá los datos según esas instrucciones, '
    f'y escribí el resultado en hedgeye_data.json. '
    f'Todos los archivos están en el directorio: {BASE}'
)

print(f'[{ts()}] ai_process: iniciando Claude Code...', flush=True)

result = subprocess.run(
    [
        CLAUDE, '-p', prompt,
        '--allowedTools', 'Read,Write',
        '--dangerously-skip-permissions',
        '--add-dir', BASE,
    ],
    timeout=420,
    cwd=BASE,
)

if result.returncode == 0:
    # Verificar que el archivo fue escrito y tiene resumen_ejecutivo
    if os.path.exists(DATA):
        with open(DATA, encoding='utf-8') as f:
            d = json.load(f)
        tiene_resumen = bool(d.get('macro_show', {}).get('resumen_ejecutivo'))
        print(f'[{ts()}] ai_process: OK — resumen_ejecutivo: {"SI" if tiene_resumen else "NO"}', flush=True)
    sys.exit(0)
else:
    print(f'[{ts()}] ai_process: ERROR (código {result.returncode})', flush=True)
    sys.exit(1)
