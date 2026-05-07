import re, json

with open('crm_offshore_cambios.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the kanban _c string
iife_start = content.find('document.getElementById("kanban-frame")')
str_end = content.rfind('";\n  var blob', 0, iife_start)
if str_end == -1:
    str_end = content.rfind('";\r\n  var blob', 0, iife_start)
str_start = content.rfind('var _c=', 0, str_end) + len('var _c=')
old_js_str = content[str_start : str_end + 1]
html = json.loads(old_js_str)

# ── 1. CSS ─────────────────────────────────────────────────────────────────
css = (
    "\n  /* ── LEAD PIPELINE ── */\n"
    "  .lead-card{background:rgba(201,168,76,.12);border:1.5px dashed rgba(201,168,76,.45);"
    "border-radius:6px;padding:8px 12px;font-size:12px;font-weight:500;color:var(--gold);"
    "cursor:grab;transition:transform .15s,opacity .15s;user-select:none;}\n"
    "  .lead-card:hover{transform:translateY(-2px);border-color:rgba(201,168,76,.7);}\n"
    "  .lead-card.dragging{opacity:.35;cursor:grabbing;}\n"
    "  .col-body.drag-over{outline:1.5px dashed rgba(201,168,76,.4);outline-offset:-2px;"
    "background-color:rgba(201,168,76,.04);}\n"
)
html = html.replace('</style>', css + '</style>', 1)

# ── 2. data-col on each col-body ────────────────────────────────────────────
cols = [
    ('01', 'Lead'),
    ('02', 'Contacto'),
    ('03', 'Reunión'),
    ('04', 'Cuenta Pershing'),
    ('07', 'Presentación de Cartera'),
    ('08', 'Fondeo'),
    ('09', 'Operaciones'),
    ('10', 'Seguimiento y Reportes'),
]
for col_id, name in cols:
    pattern = (
        r'(<span class="col-header-name">' + re.escape(name) +
        r'</span>[\s\S]*?<div class="col-body")(?! data-col)'
    )
    html = re.sub(pattern, r'\1 data-col="' + col_id + '"', html, count=1)

# Verify
found = re.findall(r'data-col="(\w+)"', html)
print(f"data-col attrs added: {found}")

# ── 3. Script before </body> ────────────────────────────────────────────────
script = """
<script>
(function(){
  var cols=document.querySelectorAll('.col-body[data-col]');
  if(!cols.length) return;
  try{
    var raw=localStorage.getItem('crm_leads');
    if(!raw) return;
    var leads=JSON.parse(raw);
    var active=leads.filter(function(l){return l.estado==='En Proceso'||l.estado==='Interesado';});
    if(!active.length) return;
    var pos={};
    try{pos=JSON.parse(localStorage.getItem('kanban_pipe_v1')||'{}');}catch(e){}
    active.forEach(function(l){
      var cid=String(pos[l.id]||'01');
      var target=document.querySelector('.col-body[data-col="'+cid+'"]')||document.querySelector('.col-body[data-col="01"]');
      if(target) target.appendChild(mkCard(l));
    });
    cols.forEach(function(col){
      col.addEventListener('dragover',function(e){e.preventDefault();col.classList.add('drag-over');});
      col.addEventListener('dragleave',function(e){if(!col.contains(e.relatedTarget))col.classList.remove('drag-over');});
      col.addEventListener('drop',function(e){
        e.preventDefault();col.classList.remove('drag-over');
        var id=parseInt(e.dataTransfer.getData('lid'));
        var card=document.querySelector('.lead-card[data-lid="'+id+'"]');
        if(card){col.appendChild(card);pos[id]=col.dataset.col;localStorage.setItem('kanban_pipe_v1',JSON.stringify(pos));}
      });
    });
  }catch(err){console.error('kanban-leads',err);}
  function mkCard(l){
    var d=document.createElement('div');
    d.className='lead-card';d.draggable=true;d.setAttribute('data-lid',l.id);
    d.textContent=l.nombre;
    d.addEventListener('dragstart',function(e){e.dataTransfer.setData('lid',String(l.id));d.classList.add('dragging');});
    d.addEventListener('dragend',function(){d.classList.remove('dragging');});
    return d;
  }
})();
</script>"""
html = html.replace('</body>', script + '\n</body>', 1)

# ── 4. Write back ────────────────────────────────────────────────────────────
new_js_str = json.dumps(html)
new_content = content[:str_start] + new_js_str + content[str_end + 1:]

with open('crm_offshore_cambios.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("OK — kanban blob actualizado")
