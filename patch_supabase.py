"""Integra Supabase realtime sync al CRM OFFSHORE."""
import os, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

# ── SQL para Supabase ──────────────────────────────────────────────────────────
SQL = """DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
  id bigint PRIMARY KEY,
  last_modified bigint NOT NULL DEFAULT 0,
  data jsonb NOT NULL DEFAULT '{}'
);
CREATE TABLE leads (
  id bigint PRIMARY KEY,
  last_modified bigint NOT NULL DEFAULT 0,
  data jsonb NOT NULL DEFAULT '{}'
);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all" ON clients FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "allow_all" ON leads FOR ALL TO anon USING (true) WITH CHECK (true);

ALTER PUBLICATION supabase_realtime ADD TABLE clients, leads;
"""

sql_path = os.path.join(BASE, '_sb_tables.sql')
with open(sql_path, 'w', encoding='utf-8') as f:
    f.write(SQL.strip())

print('=' * 60)
print('PASO 1 — Antes de continuar, correr el SQL:')
print('  Supabase → SQL Editor → New query')
print('  Pegar: _sb_tables.sql  y hacer Run')
print('=' * 60)
print()

# ── Código JS de integración Supabase ─────────────────────────────────────────
SB_JS = """
// ─── SUPABASE REALTIME SYNC ──────────────────────────────────────────────────
var _sb=null,_sbReady=false,_sbLastPull=0,_sbPulling=false;

function _initSupabase(){
  try{
    if(typeof window.supabase==='undefined'){console.warn('[SB] SDK no cargado');return;}
    _sb=window.supabase.createClient(
      'https://mgbjvbwqspeumpwprbbt.supabase.co',
      'sb_publishable_q4-FOP1jGSrEiu06LMfnDA_Q6q8sxh8'
    );
    _sbReady=true;
    _sbSubscribe();
    updateSyncStatus();
  }catch(e){console.warn('[SB] init:',e);}
}

async function _sbPush(){
  if(!_sbReady)return;
  try{
    var now=Date.now();
    var cr=clients.map(function(c){return{id:c.id,last_modified:c.lastModified||now,data:c};});
    var lr=leads.map(function(l){return{id:l.id,last_modified:l.lastModified||now,data:l};});
    if(cr.length)await _sb.from('clients').upsert(cr,{onConflict:'id'});
    if(lr.length)await _sb.from('leads').upsert(lr,{onConflict:'id'});
  }catch(e){console.warn('[SB] push:',e);}
}

async function _sbPull(silent){
  if(!_sbReady)return false;
  try{
    _sbLastPull=Date.now();
    var res=await Promise.all([
      _sb.from('clients').select('id,last_modified,data').order('id'),
      _sb.from('leads').select('id,last_modified,data').order('id')
    ]);
    var cRes=res[0],lRes=res[1];
    if(cRes.error||lRes.error){console.warn('[SB] pull err',cRes.error||lRes.error);return false;}
    var changed=false;
    var delCI=new Set(JSON.parse(localStorage.getItem('_deletedClientIds')||'[]'));
    var delLI=new Set(JSON.parse(localStorage.getItem('_deletedLeadIds')||'[]'));
    var byId={};clients.forEach(function(c){byId[c.id]=c;});
    cRes.data.forEach(function(row){
      if(delCI.has(row.id))return;
      var loc=byId[row.id];
      if(!loc){clients.push(Object.assign({},row.data,{id:row.id,lastModified:row.last_modified}));changed=true;}
      else if((row.last_modified||0)>(loc.lastModified||0)){Object.assign(loc,row.data,{id:row.id,lastModified:row.last_modified});changed=true;}
    });
    var byIdL={};leads.forEach(function(l){byIdL[l.id]=l;});
    lRes.data.forEach(function(row){
      if(delLI.has(row.id))return;
      var loc=byIdL[row.id];
      if(!loc){leads.push(Object.assign({},row.data,{id:row.id,lastModified:row.last_modified}));changed=true;}
      else if((row.last_modified||0)>(loc.lastModified||0)){Object.assign(loc,row.data,{id:row.id,lastModified:row.last_modified});changed=true;}
    });
    if(changed){_sbPulling=true;saveToStorage();_sbPulling=false;render();if(!silent)showToast('↓ Datos actualizados');updateSyncStatus();}
    return changed;
  }catch(e){console.warn('[SB] pull:',e);return false;}
}

async function _sbDelete(table,id){
  if(!_sbReady)return;
  try{await _sb.from(table).delete().eq('id',id);}catch(e){}
}

function _sbSubscribe(){
  if(!_sbReady)return;
  try{
    _sb.channel('crm-rt')
      .on('postgres_changes',{event:'*',schema:'public',table:'clients'},function(){_sbPull(true);})
      .on('postgres_changes',{event:'*',schema:'public',table:'leads'},function(){_sbPull(true);})
      .subscribe(function(s){console.log('[SB] rt:',s);});
  }catch(e){console.warn('[SB] sub:',e);}
}

function sbActualizar(){
  if(!_sbReady){showToast('Sin conexión a Supabase',true);return;}
  _sbPull(false).then(function(ch){if(!ch)showToast('Ya al día ✓');});
}

document.addEventListener('visibilitychange',function(){
  if(!document.hidden&&_sbReady&&Date.now()-_sbLastPull>180000)_sbPull(true);
});
// ─────────────────────────────────────────────────────────────────────────────
"""

# ── Lista de reemplazos (old, new) ────────────────────────────────────────────
PATCHES = [
    # 1. SDK Supabase antes de </head>
    (
        '</head>',
        '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>\n</head>'
    ),
    # 2. Insertar bloque Supabase entre showToast y saveToStorage
    (
        "  setTimeout(()=>t.classList.remove('show'),2500);\n}\nfunction saveToStorage(){",
        "  setTimeout(()=>t.classList.remove('show'),2500);\n}" + SB_JS + "\nfunction saveToStorage(){"
    ),
    # 3. saveToStorage: agregar _sbPush() fire-and-forget
    (
        "    _localModified=true;\n  }catch(e){showToast('Error al guardar: '+e.message,true);}",
        "    _localModified=true;\n    if(!_sbPulling&&_sbReady)_sbPush();\n  }catch(e){showToast('Error al guardar: '+e.message,true);}"
    ),
    # 4. mergeArr: actualizar registros existentes si Vercel tiene versión más nueva
    (
        "          var added=false;\n          snap.forEach(function(x){if(!byId[x.id]&&!delSet.has(x.id)){local.push(x);byId[x.id]=x;added=true;}});\n          return added?JSON.stringify(local):null;",
        "          var changed=false;\n          snap.forEach(function(x){\n            if(delSet.has(x.id))return;\n            if(!byId[x.id]){local.push(x);byId[x.id]=x;changed=true;}\n            else if((x.lastModified||0)>(byId[x.id].lastModified||0)){Object.assign(byId[x.id],x);changed=true;}\n          });\n          return changed?JSON.stringify(local):null;"
    ),
    # 5. saveRow: marcar timestamp en el cliente editado
    (
        "  saveToStorage();\n  showToast('Guardado ✓');\n}\nfunction saveLeadRow",
        "  c.lastModified=Date.now();\n  saveToStorage();\n  showToast('Guardado ✓');\n}\nfunction saveLeadRow"
    ),
    # 6. saveLeadRow: marcar timestamp en el lead editado
    (
        "  saveToStorage();\n  updateAutoAUM();\n  showToast('Guardado ✓');\n}\n\nfunction parseAUM",
        "  l.lastModified=Date.now();\n  saveToStorage();\n  updateAutoAUM();\n  showToast('Guardado ✓');\n}\n\nfunction parseAUM"
    ),
    # 7. save(): marcar timestamp en cliente/lead creado o editado
    (
        "  closeModal();render();saveToStorage();\n}\n\nfunction editClient",
        "  (function(){var _t=editType==='lead'?leads:clients;var _id=editId||(editType==='lead'?nextLead-1:nextId-1);var _r=_t.find(function(x){return x.id===_id;});if(_r)_r.lastModified=Date.now();})();\n  closeModal();render();saveToStorage();\n}\n\nfunction editClient"
    ),
    # 8. delClient: eliminar también de Supabase
    (
        "localStorage.setItem('_deletedClientIds',JSON.stringify(d));}catch(e){}}}",
        "localStorage.setItem('_deletedClientIds',JSON.stringify(d));}catch(e){}_sbDelete('clients',id);}}"
    ),
    # 9. delLead: eliminar también de Supabase
    (
        "localStorage.setItem('_deletedLeadIds',JSON.stringify(d));}catch(e){}}}",
        "localStorage.setItem('_deletedLeadIds',JSON.stringify(d));}catch(e){}_sbDelete('leads',id);}}"
    ),
    # 10. Botón "↓ Actualizar" en el sidebar
    (
        "Sync con Vercel</button>\n  </div>\n</div>\n<div class=\"content-area\">",
        "Sync con Vercel</button>\n    <button onclick=\"sbActualizar()\" style=\"width:100%;padding:8px 6px;background:rgba(33,160,85,.08);border:1px solid rgba(33,160,85,.2);color:#21A055;border-radius:6px;cursor:pointer;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;font-family:Inter,sans-serif;\">↓ Actualizar</button>\n  </div>\n</div>\n<div class=\"content-area\">"
    ),
    # 11. Startup: inicializar Supabase y hacer pull inicial
    (
        "renderMgr();render();\nif(sessionStorage.getItem('_hgReload')){",
        "renderMgr();render();\n_initSupabase();\nsetTimeout(function(){if(_sbReady){_sbPull(true).then(function(){_sbPush();});}},800);\nif(sessionStorage.getItem('_hgReload')){"
    ),
    # 12. updateSyncStatus: mostrar indicador Supabase + estado Vercel
    (
        "function updateSyncStatus(){\n  var el=document.getElementById('sync-status');\n  if(!el) return;\n  var ts=parseInt(localStorage.getItem('_sync_ts')||'0');\n  if(!ts){el.innerHTML='';return;}\n  var mins=Math.floor((Date.now()-ts)/60000);\n  var color=mins<10?'#A8DABB':mins<60?'#C9A84C':'#6B8578';\n  var txt=mins<1?'Sincronizado ahora':mins<60?'Sync hace '+mins+'min':'Sync hace '+Math.floor(mins/60)+'h';\n  el.innerHTML='<span class=\"sync-dot\" style=\"background:'+color+'\"></span><span style=\"color:'+color+'\">'+txt+'</span>';\n}",
        "function updateSyncStatus(){\n  var el=document.getElementById('sync-status');\n  if(!el)return;\n  var parts=[];\n  if(typeof _sbReady!=='undefined'&&_sbReady)parts.push('<span style=\"display:inline-flex;align-items:center;gap:3px;\"><span style=\"width:6px;height:6px;border-radius:50%;background:#21A055;display:inline-block;\"></span><span style=\"color:#21A055;font-size:10px;\">Realtime</span></span>');\n  var ts=parseInt(localStorage.getItem('_sync_ts')||'0');\n  if(ts){var mins=Math.floor((Date.now()-ts)/60000);var color=mins<10?'#A8DABB':mins<60?'#C9A84C':'#6B8578';var txt=mins<1?'Vercel: ahora':mins<60?'Vercel: '+mins+'m':'Vercel: '+Math.floor(mins/60)+'h';parts.push('<span style=\"color:'+color+'\">'+txt+'</span>');}\n  el.innerHTML=parts.join('<span style=\"color:#3A5A45;margin:0 4px;\">·</span>');\n}"
    ),
]

# ── Aplicar a los dos archivos HTML ───────────────────────────────────────────
for fname in ['crm_offshore_cambios.html', 'index.html']:
    path = os.path.join(BASE, fname)
    if not os.path.exists(path):
        print(f'  SKIP: {fname}')
        continue
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if 'supabase-js' in content:
        print(f'  YA APLICADO: {fname}')
        continue
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

print()
print('Listo.')
print()
print('SIGUIENTE PASO:')
print('  1. Correr el SQL de _sb_tables.sql en Supabase (si no lo hiciste)')
print('  2. git add + commit + push')
print('  3. Abrir el dashboard y verificar el punto verde "Realtime"')
