"""
Actualiza HTML + hace git push desde hedgeye_data.json ya procesado.
Usar después de que Claude Code genere el resumen ejecutivo.
"""
import os, sys, json, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hedgeye_listener import update_html_files, git_push

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'hedgeye_data.json')

if not os.path.exists(DATA):
    print("ERROR: hedgeye_data.json no encontrado.")
    sys.exit(1)

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Actualizando dashboard con data de: {data.get('updated','?')}")
hg_json = json.dumps(data, ensure_ascii=False)
update_html_files(hg_json=hg_json)
git_push(f'Hedgeye AI update {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}')
print("Listo.")
