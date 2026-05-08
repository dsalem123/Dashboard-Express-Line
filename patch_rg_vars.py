"""
Rename CSS variables in:
1. ExpressLine_ReportGenerator_v2.html  (standalone)
2. The RG blob embedded in crm_offshore_cambios.html
Map: --v→--ev  --m→--mint  --d→--gold  --c→--cream  --g→--vg
"""
import re

RENAMES = [
    ('var(--v)',  'var(--ev)'),
    ('var(--m)',  'var(--mint)'),
    ('var(--d)',  'var(--gold)'),
    ('var(--c)',  'var(--cream)'),
    ('var(--g)',  'var(--vg)'),
    # :root declarations
    ('--v:#',    '--ev:#'),
    ('--m:#',    '--mint:#'),
    ('--d:#',    '--gold:#'),
    ('--c:#',    '--cream:#'),
    ('--g:#',    '--vg:#'),
]

def apply_renames(text):
    for old, new in RENAMES:
        text = text.replace(old, new)
    return text

# ── 1. Standalone file ────────────────────────────────────────────────────────
with open('ExpressLine_ReportGenerator_v2.html', 'r', encoding='utf-8') as f:
    rg = f.read()

before = sum(rg.count(old) for old, _ in RENAMES)
rg = apply_renames(rg)
after  = sum(rg.count(new) for _, new in RENAMES)
print(f"ExpressLine_ReportGenerator_v2.html: {before} replacements applied")

with open('ExpressLine_ReportGenerator_v2.html', 'w', encoding='utf-8') as f:
    f.write(rg)

# ── 2. RG blob in crm_offshore_cambios.html ───────────────────────────────────
with open('crm_offshore_cambios.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Landmark: find rg-frame src assignment, then work backwards to find var _c=
rg_anchor = content.find('document.getElementById("rg-frame").src=URL.createObjectURL(blob)')
if rg_anchor == -1:
    print("ERROR: rg-frame anchor not found"); exit(1)

str_end   = content.rfind('";\n  var blob', 0, rg_anchor)
if str_end == -1:
    str_end = content.rfind('";\r\n  var blob', 0, rg_anchor)
if str_end == -1:
    print("ERROR: blob string end not found"); exit(1)

str_start = content.rfind('var _c=', 0, str_end) + len('var _c=')
old_js_str = content[str_start : str_end + 1]

print(f"RG blob: extracted {len(old_js_str)} chars at [{str_start}:{str_end+1}]")

# Don't json.loads — blob has \' sequences not valid in JSON.
# CSS variable names have no special chars, so replace directly on raw string.
before2 = sum(old_js_str.count(old) for old, _ in RENAMES)
new_js_str = apply_renames(old_js_str)
print(f"RG blob: {before2} replacements applied")

new_content = content[:str_start] + new_js_str + content[str_end + 1:]

with open('crm_offshore_cambios.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("OK — variables renamed in both files")
