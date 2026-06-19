"""
embed_portfolios.py
Re-embebe portfolios_online.html actualizado en crm_offshore_cambios.html e index.html
"""
import re

PFOL = r'C:/Users/usuario/Desktop/CRM OFFSHORE/portfolios_online.html'
CRM  = r'C:/Users/usuario/Desktop/CRM OFFSHORE/crm_offshore_cambios.html'
IDX  = r'C:/Users/usuario/Desktop/CRM OFFSHORE/index.html'

def js_escape(s):
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\r', '')
    s = s.replace('\n', '\\n')
    s = s.replace('</script>', '<\\/script>')
    return s

with open(PFOL, 'r', encoding='utf-8') as f:
    content = f.read()
escaped = js_escape(content)
print(f'portfolios_online.html leido: {len(content)} chars')

BLOB_MARKER = 'new Blob([_c],{type:"text/html"});\n  document.getElementById("portfolios-frame")'

for path, name in [(CRM, 'crm_offshore_cambios'), (IDX, 'index')]:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    blob_pos = html.find(BLOB_MARKER)
    if blob_pos < 0:
        print(f'{name}: BLOB_MARKER no encontrado — saltando')
        continue

    # Walk back to find the start of var _c="
    start_tag = '  var _c="'
    var_pos = html.rfind(start_tag, 0, blob_pos)
    if var_pos < 0:
        print(f'{name}: var _c=" no encontrado antes del blob marker — saltando')
        continue

    # The _c value ends at the `";` just before the blob line
    # Find the `";` that terminates the string (right before \n  var blob)
    end_tag = '";\n  var blob='
    end_pos = html.find(end_tag, var_pos)
    if end_pos < 0:
        print(f'{name}: cierre ";\n  var blob= no encontrado — saltando')
        continue

    old_line = html[var_pos : end_pos + len(end_tag)]
    new_line = start_tag + escaped + '";\n  var blob='
    html = html[:var_pos] + new_line + html[var_pos + len(old_line):]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'{name}: OK — guardado ({len(html)} chars)')
