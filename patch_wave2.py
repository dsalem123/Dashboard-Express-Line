"""Wave 2 — UX: doble-click perfil, modal borrado con undo, hint de edicion, toasts mejorados."""
import os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Nuevas funciones showToast / showToastUndo ─────────────────────────────────
SHOW_TOAST_NEW = """var _undoFns={},_undoFnId=0;
function showToast(msg,isError){
  const t=document.getElementById('toast');
  const ic=isError?'<span style="color:#f5a5a5;margin-right:7px;font-weight:700;">✗</span>':'<span style="color:var(--mint);margin-right:7px;font-weight:700;">✓</span>';
  t.innerHTML=ic+msg;
  t.className='toast'+(isError?' error':'');
  t.style.pointerEvents='none';
  void t.offsetWidth;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer=setTimeout(()=>t.classList.remove('show'),2500);
}
function showToastUndo(msg,undoFn,commitFn){
  const t=document.getElementById('toast');
  var fid=++_undoFnId;
  _undoFns[fid]=function(){t._undone=true;clearTimeout(t._timer);t.classList.remove('show');t.style.pointerEvents='none';undoFn();delete _undoFns[fid];};
  t.innerHTML='<span style="color:#f5a5a5;margin-right:7px;font-weight:700;">✗</span>'+msg+'<button onclick="_undoFns['+fid+']()" style="margin-left:12px;background:rgba(201,168,76,.15);border:1px solid rgba(201,168,76,.4);color:#C9A84C;border-radius:4px;padding:2px 9px;font-size:11px;cursor:pointer;font-family:Inter,sans-serif;letter-spacing:.5px;">Deshacer</button>';
  t.className='toast error';
  t.style.pointerEvents='auto';
  void t.offsetWidth;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._undone=false;
  t._timer=setTimeout(()=>{t.classList.remove('show');t.style.pointerEvents='none';if(!t._undone&&commitFn)commitFn();delete _undoFns[fid];},5000);
}"""

# ── Funciones delClient / delLead con undo ─────────────────────────────────────
DEL_FUNCS_NEW = """function delClient(id){
  var c=clients.find(x=>x.id===id);
  if(!c)return;
  var bk=JSON.parse(JSON.stringify(c)),nm=c.nombre;
  clients=clients.filter(x=>x.id!==id);
  render();saveToStorage();
  try{var d=JSON.parse(localStorage.getItem('_deletedClientIds')||'[]');if(!d.includes(id))d.push(id);localStorage.setItem('_deletedClientIds',JSON.stringify(d));}catch(e){}
  showToastUndo('Eliminado: '+nm,function(){
    clients.push(bk);
    try{var d=JSON.parse(localStorage.getItem('_deletedClientIds')||'[]');d=d.filter(x=>x!==id);localStorage.setItem('_deletedClientIds',JSON.stringify(d));}catch(e){}
    render();saveToStorage();showToast('Restaurado: '+nm);
  },function(){_sbDelete('clients',id);});
}
function delLead(id){
  var l=leads.find(x=>x.id===id);
  if(!l)return;
  var bk=JSON.parse(JSON.stringify(l)),nm=l.nombre;
  leads=leads.filter(x=>x.id!==id);
  render();saveToStorage();
  try{var d=JSON.parse(localStorage.getItem('_deletedLeadIds')||'[]');if(!d.includes(id))d.push(id);localStorage.setItem('_deletedLeadIds',JSON.stringify(d));}catch(e){}
  showToastUndo('Eliminado: '+nm,function(){
    leads.push(bk);
    try{var d=JSON.parse(localStorage.getItem('_deletedLeadIds')||'[]');d=d.filter(x=>x!==id);localStorage.setItem('_deletedLeadIds',JSON.stringify(d));}catch(e){}
    render();saveToStorage();showToast('Restaurado: '+nm);
  },function(){_sbDelete('leads',id);});
}"""

# ── Listener: hint de edición + Enter/Esc en celdas contenteditable ────────────
EDIT_HINT_JS = """
// Hint de edicion + Enter=guardar, Esc=cancelar
(function(){
  var _orig=null;
  document.addEventListener('focusin',function(e){
    if(e.target.matches('[contenteditable]')){
      _orig=e.target.textContent;
      var h=document.getElementById('edit-hint');
      if(h)h.style.opacity='1';
    }
  });
  document.addEventListener('focusout',function(e){
    if(e.target.matches('[contenteditable]')){
      _orig=null;
      var h=document.getElementById('edit-hint');
      if(h)h.style.opacity='0';
    }
  });
  document.addEventListener('keydown',function(e){
    var t=document.activeElement;
    if(!t||!t.matches('[contenteditable]'))return;
    if(e.key==='Enter'){
      e.preventDefault();
      var key=t.dataset.key;
      if(key){
        var mc=key.match(/^c-(\\d+)-/);
        if(mc)saveRow(parseInt(mc[1]));
        var ml=key.match(/^l-(\\d+)-/);
        if(ml)saveLeadRow(parseInt(ml[1]));
      }
      t.blur();
    } else if(e.key==='Escape'){
      if(_orig!==null)t.textContent=_orig;
      t.blur();
    }
  });
})();"""

PATCHES = [
    # 1. Toast: mover a top-right y flip la animacion
    (
        ".toast{position:fixed;bottom:28px;right:28px;",
        ".toast{position:fixed;top:28px;right:28px;"
    ),
    (
        "opacity:0;transform:translateY(10px);transition:opacity .25s,transform .25s;pointer-events:none;}",
        "opacity:0;transform:translateY(-10px);transition:opacity .25s,transform .25s;pointer-events:none;}"
    ),
    # 2. showToast: reemplazar con version con iconos + agregar showToastUndo
    (
        "function showToast(msg,isError){\n  const t=document.getElementById('toast');\n  t.textContent=msg;\n  t.className='toast'+(isError?' error':'');\n  void t.offsetWidth;\n  t.classList.add('show');\n  setTimeout(()=>t.classList.remove('show'),2500);\n}",
        SHOW_TOAST_NEW
    ),
    # 3. <tr> de clientes: doble-click abre perfil 360
    (
        "document.getElementById('tbody-clients').innerHTML=fc.length?fc.map(c=>`<tr>",
        "document.getElementById('tbody-clients').innerHTML=fc.length?fc.map(c=>`<tr ondblclick=\"if(!event.target.closest('[contenteditable]'))openPerfil(${c.id})\" title=\"Doble click: abrir Perfil 360\">"
    ),
    # 4. delClient / delLead: reemplazar con versiones con undo
    (
        "function delClient(id){if(confirm('¿Eliminar cliente?')){clients=clients.filter(c=>c.id!==id);render();saveToStorage();try{var d=JSON.parse(localStorage.getItem('_deletedClientIds')||'[]');if(!d.includes(id))d.push(id);localStorage.setItem('_deletedClientIds',JSON.stringify(d));}catch(e){}_sbDelete('clients',id);}}\nfunction delLead(id){if(confirm('¿Eliminar lead?')){leads=leads.filter(l=>l.id!==id);render();saveToStorage();try{var d=JSON.parse(localStorage.getItem('_deletedLeadIds')||'[]');if(!d.includes(id))d.push(id);localStorage.setItem('_deletedLeadIds',JSON.stringify(d));}catch(e){}_sbDelete('leads',id);}}",
        DEL_FUNCS_NEW
    ),
    # 5. Agregar div edit-hint junto al toast
    (
        '<div id="toast" class="toast"></div>',
        '<div id="toast" class="toast"></div>\n<div id="edit-hint" style="position:fixed;bottom:0;left:0;right:0;text-align:center;padding:5px;font-size:11px;font-family:\'Inter\',sans-serif;color:var(--vg);background:rgba(7,19,16,.92);border-top:1px solid rgba(168,218,187,.1);opacity:0;transition:opacity .18s;pointer-events:none;z-index:800;letter-spacing:.5px;">Enter para guardar &nbsp;&middot;&nbsp; Esc para cancelar</div>'
    ),
    # 6. Agregar listeners de hint + Enter/Esc al startup
    (
        "setInterval(updateSyncStatus,60000);",
        "setInterval(updateSyncStatus,60000);" + EDIT_HINT_JS
    ),
]

for fname in ['crm_offshore_cambios.html', 'index.html']:
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f'  SKIP: {fname}'); continue
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if 'showToastUndo' in content:
        print(f'  YA APLICADO: {fname}'); continue
    new = content
    ok = 0
    for i, (old, rep) in enumerate(PATCHES):
        if old not in new:
            print(f'  WARN patch {i+1}: marcador no encontrado en {fname}')
            continue
        new = new.replace(old, rep, 1)
        ok += 1
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    print(f'  OK: {fname}  ({ok}/{len(PATCHES)} patches aplicados)')

print('Listo.')
