"""
patch_propuesta_v2.py — Reemplaza el módulo Propuesta de Cartera completo.
"""
import re, sys

FILE = 'crm_offshore_cambios.html'
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════
# 1. REEMPLAZAR CSS
# ══════════════════════════════════════════════════════════
OLD_CSS_START = '/* ── PROPUESTA DE CARTERA ── */'
OLD_CSS_END   = '.prop-empty{padding:40px 20px;text-align:center;color:var(--vg);font-size:12px;}'

NEW_CSS = """/* ── PROPUESTA DE CARTERA ── */
#prop-pdf-stage{position:absolute;left:-9999px;top:0;width:794px;background:#0a1f1b;pointer-events:none;}
.prop-topbar{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;border-bottom:1px solid rgba(168,218,187,.1);gap:12px;flex-wrap:wrap;}
.prop-topbar-left{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}
.prop-client-sel{background:rgba(13,41,36,.8);border:1px solid rgba(168,218,187,.14);border-radius:6px;color:var(--cream);font-size:12px;padding:7px 12px;font-family:Inter,sans-serif;outline:none;min-width:200px;}
.prop-client-sel:focus{border-color:rgba(201,168,76,.4);}
.prop-btn-nueva{background:var(--gold);border:none;border-radius:6px;color:#0a1f1b;font-size:11px;font-weight:700;padding:8px 18px;cursor:pointer;font-family:Inter,sans-serif;letter-spacing:.5px;white-space:nowrap;}
.prop-btn-nueva:hover{opacity:.88;}
.prop-layout{display:flex;height:calc(100vh - 165px);gap:0;overflow:hidden;}
.prop-sidebar{width:210px;min-width:190px;border-right:1px solid rgba(168,218,187,.1);overflow-y:auto;flex-shrink:0;}
.prop-sidebar-hdr{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(168,218,187,.07);}
.prop-sidebar-hdr span{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--vg);}
.prop-list-item{padding:11px 14px;cursor:pointer;border-bottom:1px solid rgba(168,218,187,.05);transition:background .15s;border-left:3px solid transparent;}
.prop-list-item:hover{background:rgba(168,218,187,.04);}
.prop-list-item.active{background:rgba(168,218,187,.07);border-left-color:var(--gold);}
.prop-list-name{font-size:11px;color:var(--cream);font-weight:500;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:164px;}
.prop-list-client{font-size:10px;color:var(--vg);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:164px;}
.prop-list-total{font-size:10px;color:var(--gold);margin-top:3px;}
.prop-editor-area{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.prop-editor-hdr{display:flex;align-items:center;justify-content:space-between;padding:10px 20px;border-bottom:1px solid rgba(168,218,187,.08);flex-shrink:0;}
.prop-editor-hdr-left{display:flex;align-items:center;gap:10px;}
.prop-editor-title{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--vg);}
.prop-btn-pdf{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:5px;color:var(--gold);font-size:10px;font-weight:600;padding:5px 14px;cursor:pointer;font-family:Inter,sans-serif;}
.prop-btn-pdf:hover{background:rgba(201,168,76,.2);}
.prop-btn-del-prop{background:rgba(231,76,60,.07);border:1px solid rgba(231,76,60,.16);border-radius:5px;color:rgba(231,76,60,.65);font-size:11px;padding:5px 10px;cursor:pointer;}
.prop-btn-del-prop:hover{color:#e74c3c;background:rgba(231,76,60,.13);}
.prop-editor-body{flex:1;overflow-y:auto;padding:20px 24px;}
.prop-doc{background:#0c2218;border-radius:10px;padding:28px 32px;max-width:860px;}
.prop-doc-top{margin-bottom:22px;}
.prop-doc-name{font-family:'Playfair Display',serif;font-size:22px;color:var(--cream);font-weight:600;margin-bottom:4px;}
.prop-doc-name-inp{background:transparent;border:none;border-bottom:1px dashed rgba(201,168,76,.3);color:var(--cream);font-family:'Playfair Display',serif;font-size:22px;font-weight:600;outline:none;width:100%;padding-bottom:2px;}
.prop-doc-name-inp:focus{border-bottom-color:var(--gold);}
.prop-doc-meta{font-size:10px;color:var(--vg);letter-spacing:.5px;margin-top:4px;}
.prop-doc-divider{height:1px;background:rgba(168,218,187,.12);margin:18px 0;}
.prop-doc-body-row{display:flex;gap:24px;align-items:flex-start;margin-bottom:22px;}
.prop-doc-desc-col{flex:1;}
.prop-doc-desc-lbl{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:8px;display:flex;align-items:center;gap:6px;}
.prop-doc-desc-inp{width:100%;background:rgba(13,41,36,.5);border:1px solid rgba(168,218,187,.1);border-radius:6px;color:var(--cream);font-size:12px;padding:12px 14px;font-family:Inter,sans-serif;resize:vertical;min-height:120px;outline:none;line-height:1.7;box-sizing:border-box;}
.prop-doc-desc-inp:focus{border-color:rgba(201,168,76,.3);}
.prop-doc-desc-inp::placeholder{color:var(--vg);}
.prop-doc-chart-col{width:220px;flex-shrink:0;text-align:center;}
.prop-doc-chart-lbl{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
.prop-comp-lbl{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.prop-comp-table{width:100%;border-collapse:collapse;}
.prop-comp-table th{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--vg);font-weight:700;padding:7px 10px;border-bottom:2px solid rgba(168,218,187,.1);text-align:left;}
.prop-comp-table th:nth-child(3){text-align:right;width:90px;}
.prop-comp-table th:nth-child(4){width:30px;}
.prop-comp-row td{padding:7px 10px;border-bottom:1px solid rgba(168,218,187,.05);vertical-align:middle;}
.prop-comp-dot{width:10px;height:10px;border-radius:2px;display:inline-block;flex-shrink:0;}
.prop-comp-num{font-size:10px;color:var(--vg);font-weight:600;min-width:18px;}
.prop-comp-name-inp{background:transparent;border:none;border-bottom:1px solid rgba(168,218,187,.1);color:var(--cream);font-size:12px;padding:3px 0;font-family:Inter,sans-serif;outline:none;width:100%;}
.prop-comp-name-inp:focus{border-bottom-color:rgba(201,168,76,.4);}
.prop-comp-name-inp::placeholder{color:rgba(107,133,120,.5);}
.prop-pct-wrap{display:flex;align-items:center;justify-content:flex-end;gap:4px;}
.prop-comp-pct-inp{background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.1);border-radius:4px;color:var(--cream);font-size:12px;font-weight:600;padding:4px 8px;font-family:Inter,sans-serif;outline:none;width:56px;text-align:right;}
.prop-comp-pct-inp:focus{border-color:rgba(201,168,76,.4);}
.prop-comp-pct-sym{font-size:11px;color:var(--vg);}
.prop-btn-row-del{background:none;border:none;color:rgba(231,76,60,.35);font-size:16px;cursor:pointer;padding:2px 4px;border-radius:3px;line-height:1;}
.prop-btn-row-del:hover{color:#e74c3c;background:rgba(231,76,60,.1);}
.prop-btn-add-row{background:none;border:none;color:var(--mint);font-size:11px;cursor:pointer;padding:10px 0 4px;font-family:Inter,sans-serif;letter-spacing:.3px;display:flex;align-items:center;gap:6px;}
.prop-btn-add-row:hover{color:var(--cream);}
.prop-comp-footer{display:flex;align-items:center;justify-content:space-between;padding:10px 10px 0;border-top:1px solid rgba(168,218,187,.1);margin-top:6px;}
.prop-comp-count{font-size:10px;color:var(--vg);}
.prop-comp-total{font-family:'Playfair Display',serif;font-size:22px;font-weight:700;}
.prop-empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:var(--vg);}
.prop-empty-state p{font-size:13px;letter-spacing:.5px;}
/* Modal */
.prop-modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:200;align-items:center;justify-content:center;}
.prop-modal-bg.open{display:flex;}
.prop-modal{background:#0e2822;border:1px solid rgba(168,218,187,.15);border-radius:12px;width:520px;max-width:95vw;max-height:90vh;overflow-y:auto;padding:28px 30px;}
.prop-modal-title{font-family:'Playfair Display',serif;font-size:20px;color:var(--cream);font-weight:600;margin-bottom:4px;}
.prop-modal-sub{font-size:11px;color:var(--vg);margin-bottom:22px;}
.prop-modal-lbl{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--vg);margin-bottom:7px;display:flex;align-items:center;gap:6px;}
.prop-modal-inp{width:100%;background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.15);border-radius:7px;color:var(--cream);font-size:13px;padding:11px 14px;font-family:Inter,sans-serif;outline:none;box-sizing:border-box;margin-bottom:18px;}
.prop-modal-inp:focus{border-color:rgba(201,168,76,.5);}
.prop-modal-inp::placeholder{color:rgba(107,133,120,.6);}
.prop-modal-comp-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}
.prop-btn-distrib{background:rgba(168,218,187,.07);border:1px solid rgba(168,218,187,.15);border-radius:5px;color:var(--mint);font-size:10px;padding:5px 12px;cursor:pointer;font-family:Inter,sans-serif;}
.prop-btn-distrib:hover{background:rgba(168,218,187,.12);}
.prop-modal-rows{display:flex;flex-direction:column;gap:8px;margin-bottom:10px;}
.prop-modal-row{display:flex;align-items:center;gap:10px;}
.prop-modal-row-num{font-size:11px;color:var(--vg);font-weight:600;min-width:18px;text-align:center;}
.prop-modal-row-name{flex:1;background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:6px;color:var(--cream);font-size:12px;padding:8px 12px;font-family:Inter,sans-serif;outline:none;}
.prop-modal-row-name:focus{border-color:rgba(201,168,76,.4);}
.prop-modal-row-name::placeholder{color:rgba(107,133,120,.5);}
.prop-modal-row-pct{width:60px;background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:6px;color:var(--cream);font-size:12px;padding:8px 8px;font-family:Inter,sans-serif;outline:none;text-align:right;}
.prop-modal-row-pct:focus{border-color:rgba(201,168,76,.4);}
.prop-modal-row-sym{font-size:11px;color:var(--vg);}
.prop-modal-row-del{background:none;border:none;color:rgba(231,76,60,.4);font-size:17px;cursor:pointer;padding:2px 4px;border-radius:3px;line-height:1;}
.prop-modal-row-del:hover{color:#e74c3c;}
.prop-modal-add-row{background:none;border:none;color:var(--mint);font-size:11px;cursor:pointer;padding:8px 0;font-family:Inter,sans-serif;display:flex;align-items:center;gap:6px;}
.prop-modal-add-row:hover{color:var(--cream);}
.prop-modal-footer-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:rgba(13,41,36,.5);border-radius:7px;margin:14px 0 20px;}
.prop-modal-count{font-size:11px;color:var(--vg);}
.prop-modal-total{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;}
.prop-modal-btns{display:flex;gap:10px;justify-content:flex-end;}
.prop-btn-cancel{background:rgba(168,218,187,.06);border:1px solid rgba(168,218,187,.14);border-radius:7px;color:var(--vg);font-size:12px;padding:10px 22px;cursor:pointer;font-family:Inter,sans-serif;}
.prop-btn-cancel:hover{color:var(--cream);}
.prop-btn-crear{background:var(--gold);border:none;border-radius:7px;color:#0a1f1b;font-size:12px;font-weight:700;padding:10px 26px;cursor:pointer;font-family:Inter,sans-serif;}
.prop-btn-crear:hover{opacity:.88;}"""

old_block_start = html.find(OLD_CSS_START)
old_block_end   = html.find(OLD_CSS_END)
if old_block_start < 0 or old_block_end < 0:
    print('ERROR: no se encontró el bloque CSS anterior'); sys.exit(1)
old_block_end += len(OLD_CSS_END)
html = html[:old_block_start] + NEW_CSS + html[old_block_end:]
print('OK CSS reemplazado')

# ══════════════════════════════════════════════════════════
# 2. REEMPLAZAR HTML
# ══════════════════════════════════════════════════════════
OLD_HTML_START = '<div id="page-propuesta" class="page">'
OLD_HTML_END   = '  <div id="prop-pdf-stage"></div>\n</div>'

NEW_HTML = """<div id="page-propuesta" class="page">
  <div class="doc-header">
    <div>
      <div class="logo-wordmark">ExpressLine</div>
      <div class="header-title">Propuesta de Cartera</div>
      <div class="gold-line"></div>
      <div class="header-sub">Offshore &middot; Gesti&oacute;n de carteras para clientes</div>
    </div>
    <span class="badge">Propuesta &middot; Offshore</span>
  </div>

  <div class="prop-topbar">
    <div class="prop-topbar-left">
      <select id="prop-client-sel" class="prop-client-sel" onchange="propSetClient(this.value)">
        <option value="">— Seleccionar cliente —</option>
      </select>
    </div>
    <button class="prop-btn-nueva" onclick="propOpenModal()">+ Nueva Cartera</button>
  </div>

  <div class="prop-layout">
    <div class="prop-sidebar">
      <div class="prop-sidebar-hdr"><span>Carteras</span></div>
      <div id="prop-list"></div>
    </div>

    <div class="prop-editor-area">
      <div class="prop-editor-hdr">
        <div class="prop-editor-hdr-left">
          <span class="prop-editor-title">Editor de Propuesta</span>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="prop-btn-pdf" onclick="propDownloadPDF()">&#11015; Descargar PDF</button>
          <button class="prop-btn-del-prop" onclick="propDeleteActive()" title="Eliminar cartera">&#128465;</button>
        </div>
      </div>
      <div class="prop-editor-body" id="prop-editor-body">
        <div class="prop-empty-state" id="prop-empty-state">
          <div style="font-size:32px;opacity:.3;">&#128196;</div>
          <p>Seleccion&#225; un cliente y cre&#225; una cartera</p>
          <button class="prop-btn-nueva" onclick="propOpenModal()">+ Nueva Cartera</button>
        </div>
        <div class="prop-doc" id="prop-doc" style="display:none;">
          <div class="prop-doc-top">
            <input id="prop-doc-name" class="prop-doc-name-inp" type="text" placeholder="Nombre de la cartera" onblur="propSetName(this.value)">
            <div class="prop-doc-meta" id="prop-doc-meta"></div>
          </div>
          <div class="prop-doc-divider"></div>
          <div class="prop-doc-body-row">
            <div class="prop-doc-desc-col">
              <div class="prop-doc-desc-lbl">&#9654; Descripci&oacute;n</div>
              <textarea id="prop-doc-desc" class="prop-doc-desc-inp" placeholder="Descrip&oacute; el perfil del inversor, objetivos y horizonte temporal..."></textarea>
            </div>
            <div class="prop-doc-chart-col">
              <div class="prop-doc-chart-lbl">Distribuci&oacute;n por activo</div>
              <div id="prop-chart-svg"></div>
              <div id="prop-legend"></div>
            </div>
          </div>
          <div class="prop-doc-divider"></div>
          <div class="prop-comp-lbl">&#9654; Composici&oacute;n</div>
          <table class="prop-comp-table">
            <thead><tr>
              <th style="width:12px;"></th>
              <th style="width:22px;">#</th>
              <th>Nombre / Ticker</th>
              <th style="text-align:right;">%</th>
              <th></th>
            </tr></thead>
            <tbody id="prop-comp-body"></tbody>
          </table>
          <button class="prop-btn-add-row" onclick="propAddAsset()">&#43; Agregar instrumento</button>
          <div class="prop-comp-footer">
            <span class="prop-comp-count" id="prop-comp-count">0 instrumentos</span>
            <span class="prop-comp-total" id="prop-comp-total">0.0%</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Nueva Cartera -->
  <div class="prop-modal-bg" id="prop-modal-bg" onclick="if(event.target===this)propCloseModal()">
    <div class="prop-modal">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px;">
        <div>
          <div class="prop-modal-title">Nueva Cartera</div>
          <div class="prop-modal-sub">Cre&#225; una cartera seleccionando instrumentos y su asignaci&#243;n.</div>
        </div>
        <button onclick="propCloseModal()" style="background:none;border:none;color:var(--vg);font-size:20px;cursor:pointer;padding:0 0 0 10px;line-height:1;">&times;</button>
      </div>
      <div class="prop-modal-lbl">&#128196; Nombre de la Cartera</div>
      <input id="prop-modal-name" class="prop-modal-inp" type="text" placeholder="Ej: Cartera Balanceada 2026">
      <div class="prop-modal-lbl">Descripci&#243;n (opcional)</div>
      <textarea id="prop-modal-desc" class="prop-modal-inp" rows="3" placeholder="Breve descripci&#243;n del objetivo de inversi&#243;n..." style="resize:vertical;"></textarea>
      <div class="prop-modal-comp-hdr">
        <div class="prop-modal-lbl" style="margin-bottom:0;">&#9202; Composici&#243;n</div>
        <button class="prop-btn-distrib" onclick="propDistributeEqual()">&#9881; Distribuir igual</button>
      </div>
      <div class="prop-modal-rows" id="prop-modal-rows"></div>
      <button class="prop-modal-add-row" onclick="propModalAddRow()">&#43; Agregar instrumento</button>
      <div class="prop-modal-footer-bar">
        <span class="prop-modal-count" id="prop-modal-count">0 instrumentos asignados</span>
        <span class="prop-modal-total" id="prop-modal-total" style="color:var(--vg);">0.0%</span>
      </div>
      <div class="prop-modal-btns">
        <button class="prop-btn-cancel" onclick="propCloseModal()">Cancelar</button>
        <button class="prop-btn-crear" onclick="propCreateFromModal()">Crear Cartera</button>
      </div>
    </div>
  </div>

  <div id="prop-pdf-stage"></div>
</div>"""

start_idx = html.find(OLD_HTML_START)
if start_idx < 0:
    print('ERROR: no se encontró page-propuesta HTML'); sys.exit(1)
end_idx = html.find(OLD_HTML_END, start_idx)
if end_idx < 0:
    print('ERROR: no se encontró el cierre del HTML'); sys.exit(1)
end_idx += len(OLD_HTML_END)
html = html[:start_idx] + NEW_HTML + html[end_idx:]
print('OK HTML reemplazado')

# ══════════════════════════════════════════════════════════
# 3. REEMPLAZAR JS
# ══════════════════════════════════════════════════════════
OLD_JS_START = '// ════════════════════════════════════════════════════════\n// PROPUESTA DE CARTERA'
OLD_JS_END   = '  return html;\n}\n'  # end of propBuildPDFHTML

NEW_JS = """// ════════════════════════════════════════════════════════
// PROPUESTA DE CARTERA
// ════════════════════════════════════════════════════════
var PROP={proposals:[],activeId:null};
var PROP_COLORS=['#A8DABB','#C9A84C','#5B9BD5','#F59E0B','#8B5CF6','#EF4444','#14B8A6','#F97316','#EC4899','#84CC16'];

function propEsc(s){return s==null?'':String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

function initPropuesta(){
  try{PROP.proposals=JSON.parse(localStorage.getItem('crm_propuestas')||'[]');}catch(e){PROP.proposals=[];}
  var clients=[];try{clients=JSON.parse(localStorage.getItem('crm_clients')||'[]');}catch(e){}
  var sel=document.getElementById('prop-client-sel');
  if(sel){
    sel.innerHTML='<option value="">— Seleccionar cliente —</option>'+
      clients.map(function(c){return '<option value="'+propEsc(c.nombre)+'">'+propEsc(c.nombre)+'</option>';}).join('');
  }
  propRenderSidebar();
  if(PROP.activeId) propRenderEditor();
}

function propSave(){try{localStorage.setItem('crm_propuestas',JSON.stringify(PROP.proposals));}catch(e){}}
function propActive(){return PROP.proposals.find(function(p){return p.id===PROP.activeId;})||null;}

function propSetClient(val){
  propRenderSidebar(val);
}

function propRenderSidebar(filterClient){
  var sel=document.getElementById('prop-client-sel');
  var client=filterClient!=null?filterClient:(sel?sel.value:'');
  var el=document.getElementById('prop-list');if(!el)return;
  var list=client?PROP.proposals.filter(function(p){return p.clientName===client;}):PROP.proposals;
  if(!list.length){
    el.innerHTML='<div style="padding:16px 14px;font-size:11px;color:var(--vg);">'+
      (client?'Sin carteras para este cliente':'Seleccion&#225; un cliente')+'</div>';
    return;
  }
  el.innerHTML=list.map(function(p){
    var total=p.assets.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
    return '<div class="prop-list-item'+(p.id===PROP.activeId?' active':'')+'" onclick="propSelect(\''+propEsc(p.id)+'\')">'+
      '<div class="prop-list-name">'+propEsc(p.name)+'</div>'+
      '<div class="prop-list-client">'+propEsc(p.clientName||'Sin cliente')+'</div>'+
      '<div class="prop-list-total">'+total.toFixed(1)+'%</div>'+
    '</div>';
  }).join('');
}

function propSelect(id){
  PROP.activeId=id;
  var p=propActive();
  if(p){
    var sel=document.getElementById('prop-client-sel');
    if(sel&&p.clientName)sel.value=p.clientName;
  }
  propRenderSidebar();
  propRenderEditor();
}

function propDeleteActive(){
  var p=propActive();if(!p)return;
  if(!confirm('¿Eliminar "'+p.name+'"?'))return;
  PROP.proposals=PROP.proposals.filter(function(x){return x.id!==p.id;});
  PROP.activeId=null;
  propSave();
  propRenderSidebar();
  document.getElementById('prop-doc').style.display='none';
  document.getElementById('prop-empty-state').style.display='flex';
}

function propRenderEditor(){
  var p=propActive();
  var doc=document.getElementById('prop-doc');
  var empty=document.getElementById('prop-empty-state');
  if(!p){
    if(doc)doc.style.display='none';
    if(empty)empty.style.display='flex';
    return;
  }
  if(doc)doc.style.display='block';
  if(empty)empty.style.display='none';
  var ni=document.getElementById('prop-doc-name');if(ni)ni.value=p.name;
  var meta=document.getElementById('prop-doc-meta');
  if(meta)meta.textContent=(p.clientName||'—')+' · '+( p.createdAt||'');
  var di=document.getElementById('prop-doc-desc');
  if(di){
    di.value=p.description||'';
    di.oninput=function(){var pp=propActive();if(pp){pp.description=this.value;propSave();}};
  }
  propRenderComp();
  propRenderChart();
}

function propRenderComp(){
  var p=propActive();if(!p)return;
  var tb=document.getElementById('prop-comp-body');if(!tb)return;
  tb.innerHTML=p.assets.map(function(a,i){
    var col=PROP_COLORS[i%PROP_COLORS.length];
    return '<tr class="prop-comp-row">'+
      '<td><span class="prop-comp-dot" style="background:'+col+';"></span></td>'+
      '<td><span class="prop-comp-num">'+(i+1)+'</span></td>'+
      '<td><input class="prop-comp-name-inp" type="text" value="'+propEsc(a.name||'')+'" placeholder="Activo o ticker..."'+
        ' onchange="propUpdateAsset('+i+',\'name\',this.value)"></td>'+
      '<td><div class="prop-pct-wrap">'+
        '<input class="prop-comp-pct-inp" type="number" min="0" max="100" step="0.1" value="'+propEsc(String(a.pct||''))+'"'+
        ' placeholder="0" onchange="propUpdateAsset('+i+',\'pct\',this.value)">'+
        '<span class="prop-comp-pct-sym">%</span>'+
      '</div></td>'+
      '<td><button class="prop-btn-row-del" onclick="propRemoveAsset('+i+')">&times;</button></td>'+
    '</tr>';
  }).join('');
  var total=p.assets.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
  var ok=Math.abs(total-100)<0.01,over=total>100;
  var col=ok?'#2ecc71':over?'#e74c3c':'var(--vg)';
  var ct=document.getElementById('prop-comp-total');
  if(ct){ct.textContent=total.toFixed(1)+'%';ct.style.color=col;}
  var cc=document.getElementById('prop-comp-count');
  if(cc)cc.textContent=p.assets.length+' instrumento'+(p.assets.length!==1?'s':'');
}

function propUpdateAsset(idx,field,val){
  var p=propActive();if(!p)return;
  p.assets[idx][field]=field==='pct'?parseFloat(val)||0:val;
  propSave();
  propRenderChart();
  propRenderComp();
}

function propAddAsset(){
  var p=propActive();if(!p)return;
  p.assets.push({name:'',pct:0});
  propSave();
  propRenderComp();
  propRenderChart();
  setTimeout(function(){
    var rows=document.querySelectorAll('.prop-comp-row');
    if(rows.length){var inp=rows[rows.length-1].querySelector('.prop-comp-name-inp');if(inp)inp.focus();}
  },40);
}

function propRemoveAsset(idx){
  var p=propActive();if(!p)return;
  p.assets.splice(idx,1);
  propSave();propRenderComp();propRenderChart();
}

function propSetName(val){
  var p=propActive();if(!p)return;
  p.name=val||'Sin nombre';
  propSave();propRenderSidebar();
}

function propBuildSVG(assets,size){
  size=size||200;
  var cx=size/2,cy=size/2,r=size*0.41,ri=size*0.20;
  var valid=assets.filter(function(a){return (parseFloat(a.pct)||0)>0;});
  var total=valid.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
  if(!total||!valid.length){
    return '<svg width="'+size+'" height="'+size+'" viewBox="0 0 '+size+' '+size+'">'+
      '<circle cx="'+cx+'" cy="'+cy+'" r="'+r+'" fill="#1a3530"/>'+
      '<circle cx="'+cx+'" cy="'+cy+'" r="'+ri+'" fill="#0a1f1b"/>'+
      '<text x="'+cx+'" y="'+(cy+4)+'" text-anchor="middle" fill="#6B8578" font-size="11" font-family="Inter,sans-serif">Sin activos</text>'+
      '</svg>';
  }
  var paths='';var angle=-Math.PI/2;
  valid.forEach(function(a,i){
    var slice=(parseFloat(a.pct)/total)*Math.PI*2;
    if(slice>=Math.PI*2-0.001)slice=Math.PI*2-0.001;
    var x1o=(cx+r*Math.cos(angle)).toFixed(2),y1o=(cy+r*Math.sin(angle)).toFixed(2);
    var x1i=(cx+ri*Math.cos(angle)).toFixed(2),y1i=(cy+ri*Math.sin(angle)).toFixed(2);
    var ea=angle+slice;
    var x2o=(cx+r*Math.cos(ea)).toFixed(2),y2o=(cy+r*Math.sin(ea)).toFixed(2);
    var x2i=(cx+ri*Math.cos(ea)).toFixed(2),y2i=(cy+ri*Math.sin(ea)).toFixed(2);
    var lg=slice>Math.PI?1:0;
    paths+='<path d="M'+x1o+','+y1o+' A'+r+','+r+' 0 '+lg+',1 '+x2o+','+y2o+
      ' L'+x2i+','+y2i+' A'+ri+','+ri+' 0 '+lg+',0 '+x1i+','+y1i+' Z"'+
      ' fill="'+PROP_COLORS[i%PROP_COLORS.length]+'" stroke="#0a1f1b" stroke-width="2"/>';
    angle=ea;
  });
  var fs=(size*0.09).toFixed(0),fs2=(size*0.037).toFixed(0);
  return '<svg width="'+size+'" height="'+size+'" viewBox="0 0 '+size+' '+size+'">'+
    paths+
    '<circle cx="'+cx+'" cy="'+cy+'" r="'+(ri-1)+'" fill="#0c2218"/>'+
    '<text x="'+cx+'" y="'+(cy-5)+'" text-anchor="middle" fill="#ECEDE3" font-size="'+fs+'" font-weight="700" font-family="\'Playfair Display\',serif">'+total.toFixed(1)+'%</text>'+
    '<text x="'+cx+'" y="'+(cy+11)+'" text-anchor="middle" fill="#6B8578" font-size="'+fs2+'" font-family="Inter,sans-serif" letter-spacing="1.5">TOTAL</text>'+
    '</svg>';
}

function propRenderChart(){
  var p=propActive();if(!p)return;
  var el=document.getElementById('prop-chart-svg');if(!el)return;
  el.innerHTML=propBuildSVG(p.assets,190);
  var leg=document.getElementById('prop-legend');if(!leg)return;
  var valid=p.assets.filter(function(a){return (parseFloat(a.pct)||0)>0;});
  if(!valid.length){leg.innerHTML='';return;}
  leg.innerHTML='<div style="margin-top:10px;">'+valid.map(function(a,i){
    return '<div style="display:flex;align-items:center;gap:7px;padding:4px 0;border-bottom:1px solid rgba(168,218,187,.05);">'+
      '<div style="width:8px;height:8px;border-radius:2px;background:'+PROP_COLORS[i%PROP_COLORS.length]+';flex-shrink:0;"></div>'+
      '<div style="flex:1;font-size:10px;color:var(--cream);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+propEsc(a.name||'—')+'</div>'+
      '<div style="font-size:10px;font-weight:700;color:var(--gold);">'+a.pct+'%</div>'+
    '</div>';
  }).join('')+'</div>';
}

// ── MODAL ──
function propOpenModal(){
  var sel=document.getElementById('prop-client-sel');
  if(sel&&!sel.value){showToast('Seleccioná un cliente primero',true);return;}
  document.getElementById('prop-modal-name').value='';
  document.getElementById('prop-modal-desc').value='';
  document.getElementById('prop-modal-rows').innerHTML='';
  propModalAddRow();propModalAddRow();
  propModalUpdateTotal();
  document.getElementById('prop-modal-bg').classList.add('open');
  setTimeout(function(){document.getElementById('prop-modal-name').focus();},100);
}

function propCloseModal(){document.getElementById('prop-modal-bg').classList.remove('open');}

function propModalAddRow(){
  var cont=document.getElementById('prop-modal-rows');if(!cont)return;
  var idx=cont.children.length;
  var div=document.createElement('div');
  div.className='prop-modal-row';
  div.setAttribute('data-idx',idx);
  div.innerHTML=
    '<span class="prop-modal-row-num">'+(idx+1)+'</span>'+
    '<input class="prop-modal-row-name" type="text" placeholder="Buscar por nombre, ticker o código..." oninput="propModalUpdateTotal()">'+
    '<input class="prop-modal-row-pct" type="number" min="0" max="100" step="0.1" placeholder="0" oninput="propModalUpdateTotal()">'+
    '<span class="prop-modal-row-sym">%</span>'+
    '<button class="prop-modal-row-del" onclick="propModalRemoveRow(this)">&times;</button>';
  cont.appendChild(div);
  propModalRenumber();
}

function propModalRemoveRow(btn){
  btn.closest('.prop-modal-row').remove();
  propModalRenumber();
  propModalUpdateTotal();
}

function propModalRenumber(){
  var rows=document.querySelectorAll('#prop-modal-rows .prop-modal-row');
  rows.forEach(function(r,i){var n=r.querySelector('.prop-modal-row-num');if(n)n.textContent=i+1;});
}

function propModalUpdateTotal(){
  var rows=document.querySelectorAll('#prop-modal-rows .prop-modal-row');
  var total=0,count=0;
  rows.forEach(function(r){
    var name=r.querySelector('.prop-modal-row-name').value.trim();
    var pct=parseFloat(r.querySelector('.prop-modal-row-pct').value)||0;
    total+=pct;if(name)count++;
  });
  var ok=Math.abs(total-100)<0.01,over=total>100;
  var col=ok?'#2ecc71':over?'#e74c3c':'var(--vg)';
  var tt=document.getElementById('prop-modal-total');
  if(tt){tt.textContent=total.toFixed(1)+'%';tt.style.color=col;}
  var cc=document.getElementById('prop-modal-count');
  if(cc)cc.textContent=count+' instrumento'+(count!==1?'s':'')+' asignados';
}

function propDistributeEqual(){
  var rows=document.querySelectorAll('#prop-modal-rows .prop-modal-row');
  if(!rows.length)return;
  var each=(100/rows.length).toFixed(1);
  rows.forEach(function(r){r.querySelector('.prop-modal-row-pct').value=each;});
  propModalUpdateTotal();
}

function propCreateFromModal(){
  var name=document.getElementById('prop-modal-name').value.trim();
  if(!name){document.getElementById('prop-modal-name').focus();showToast('Ingresá un nombre',true);return;}
  var sel=document.getElementById('prop-client-sel');
  var clientName=sel?sel.value:'';
  var desc=document.getElementById('prop-modal-desc').value.trim();
  var rows=document.querySelectorAll('#prop-modal-rows .prop-modal-row');
  var assets=[];
  rows.forEach(function(r){
    var n=r.querySelector('.prop-modal-row-name').value.trim();
    var pct=parseFloat(r.querySelector('.prop-modal-row-pct').value)||0;
    if(n||pct)assets.push({name:n,pct:pct});
  });
  var id='prop_'+Date.now();
  var today=new Date().toLocaleDateString('es-AR',{day:'2-digit',month:'long',year:'numeric'});
  PROP.proposals.unshift({id:id,clientName:clientName,name:name,description:desc,assets:assets,createdAt:today});
  PROP.activeId=id;
  propSave();
  propCloseModal();
  propRenderSidebar();
  propRenderEditor();
  showToast('Cartera creada');
}

// ── PDF ──
function propDownloadPDF(){
  var p=propActive();if(!p){showToast('No hay cartera activa',true);return;}
  var stage=document.getElementById('prop-pdf-stage');
  stage.innerHTML=propBuildPDFHTML(p);
  showToast('Generando PDF...');
  setTimeout(function(){
    html2canvas(stage,{scale:1.8,backgroundColor:'#0a1f1b',useCORS:true,logging:false,
      width:794,windowWidth:794,scrollX:0,scrollY:-window.scrollY,
      onclone:function(doc){var s=doc.getElementById('prop-pdf-stage');if(s){s.style.left='0';s.style.position='relative';}}
    }).then(function(canvas){
      var pageW=210,pageH=Math.round((canvas.height/canvas.width)*pageW*100)/100;
      var doc=new jspdf.jsPDF({orientation:'p',unit:'mm',format:[pageW,pageH]});
      doc.addImage(canvas.toDataURL('image/jpeg',0.92),'JPEG',0,0,pageW,pageH);
      doc.save('Propuesta_'+(p.clientName||'cliente').replace(/[^a-zA-Z0-9]/g,'_')+'_'+new Date().toISOString().split('T')[0]+'.pdf');
      stage.innerHTML='';showToast('PDF descargado');
    }).catch(function(e){showToast('Error al generar PDF',true);stage.innerHTML='';});
  },300);
}

function propBuildPDFHTML(p){
  var BG='#0a1f1b',CARD='#0c2218',BORDER='#1d3a35',GOLD='#C9A84C',MINT='#A8DABB',CREAM='#ECEDE3',MUTED='#6B8578';
  var today=new Date().toLocaleDateString('es-AR',{day:'2-digit',month:'long',year:'numeric'});
  var valid=p.assets.filter(function(a){return (parseFloat(a.pct)||0)>0;});
  var total=valid.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
  var svgChart=propBuildSVG(valid,240);
  var thS='padding:8px 10px;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:'+MUTED+';font-weight:700;border-bottom:2px solid '+BORDER+';';
  var rowsHTML=valid.map(function(a,i){
    var col=PROP_COLORS[i%PROP_COLORS.length];
    return '<tr>'+
      '<td style="padding:8px 10px;"><div style="width:10px;height:10px;border-radius:2px;background:'+col+';"></div></td>'+
      '<td style="padding:8px 10px;font-size:10px;color:'+MUTED+';font-weight:600;">'+(i+1)+'</td>'+
      '<td style="padding:8px 10px;font-size:12px;color:'+CREAM+';">'+propEsc(a.name)+'</td>'+
      '<td style="padding:8px 10px;font-size:14px;font-weight:700;color:'+CREAM+';text-align:right;font-family:\'Playfair Display\',serif;">'+a.pct+'%</td>'+
    '</tr>';
  }).join('');
  var html='<div style="background:'+BG+';padding:44px 48px 40px;font-family:Inter,sans-serif;color:'+CREAM+';width:794px;box-sizing:border-box;line-height:1.4;">';
  html+='<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:4px;"><tr>'+
    '<td style="vertical-align:bottom;background:'+BG+';">'+
      '<div style="font-family:\'Playfair Display\',serif;font-size:27px;color:'+GOLD+';letter-spacing:3px;font-weight:600;">EXPRESSLINE</div>'+
      '<div style="font-size:9px;letter-spacing:3px;color:'+MUTED+';margin-top:4px;text-transform:uppercase;">Dashboard Offshore</div>'+
      '<div style="width:40px;height:2px;background:'+GOLD+';margin-top:9px;"></div>'+
    '</td>'+
    '<td style="text-align:right;vertical-align:bottom;background:'+BG+';">'+
      '<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:'+MUTED+';">Propuesta de Cartera</div>'+
      '<div style="font-size:11px;color:'+MINT+';margin-top:5px;">'+today+'</div>'+
    '</td>'+
  '</tr></table>'+
  '<div style="height:1px;background:'+BORDER+';margin-bottom:26px;margin-top:20px;"></div>';
  html+='<div style="margin-bottom:8px;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:'+MUTED+';">Cliente</div>'+
    '<div style="font-family:\'Playfair Display\',serif;font-size:26px;color:'+CREAM+';font-weight:600;">'+(p.clientName||'—').toUpperCase()+'</div>'+
    '<div style="font-size:13px;color:'+GOLD+';margin-top:5px;letter-spacing:.5px;">'+propEsc(p.name)+'</div>'+
    '<div style="width:50px;height:2px;background:'+GOLD+';margin-top:10px;margin-bottom:22px;"></div>';
  if(p.description){
    html+='<div style="background:'+CARD+';border-radius:8px;padding:18px 22px;margin-bottom:20px;">'+
      '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:10px;">Descripción</div>'+
      '<div style="font-size:12px;color:'+CREAM+';line-height:1.8;">'+propEsc(p.description).replace(/\n/g,'<br>')+'</div>'+
    '</div>';
  }
  html+='<table width="100%" cellpadding="0" cellspacing="0"><tr>'+
    '<td width="42%" style="vertical-align:top;background:'+BG+';padding-right:16px;">'+
      '<div style="background:'+CARD+';border-radius:8px;padding:20px;text-align:center;">'+
        '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid '+BORDER+';">Distribución por activo</div>'+
        svgChart+
      '</div>'+
    '</td>'+
    '<td width="58%" style="vertical-align:top;background:'+BG+';">'+
      '<div style="background:'+CARD+';border-radius:8px;padding:20px;">'+
        '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid '+BORDER+';">Composición</div>'+
        '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">'+
          '<thead><tr>'+
            '<th style="'+thS+'width:16px;"></th>'+
            '<th style="'+thS+'width:22px;text-align:left;">#</th>'+
            '<th style="'+thS+'text-align:left;">Activo</th>'+
            '<th style="'+thS+'text-align:right;">%</th>'+
          '</tr></thead>'+
          '<tbody>'+rowsHTML+'</tbody>'+
          '<tfoot><tr>'+
            '<td colspan="3" style="padding:10px;border-top:1px solid '+BORDER+';font-size:9px;letter-spacing:1px;text-transform:uppercase;color:'+GOLD+';font-weight:700;">Total</td>'+
            '<td style="padding:10px;border-top:1px solid '+BORDER+';text-align:right;font-size:16px;font-weight:700;color:'+GOLD+';font-family:\'Playfair Display\',serif;">'+total.toFixed(1)+'%</td>'+
          '</tr></tfoot>'+
        '</table>'+
      '</div>'+
    '</td>'+
  '</tr></table>';
  html+='<div style="height:1px;background:'+BORDER+';margin-top:24px;margin-bottom:14px;"></div>'+
  '<table width="100%" cellpadding="0" cellspacing="0"><tr>'+
    '<td style="font-size:9px;color:#3a5a52;letter-spacing:1.5px;text-transform:uppercase;background:'+BG+';">Express Line &middot; Propuesta Confidencial</td>'+
    '<td style="text-align:right;font-size:9px;color:#3a5a52;background:'+BG+';">Generado el '+today+'</td>'+
  '</tr></table></div>';
  return html;
}
"""

js_start = html.find(OLD_JS_START)
if js_start < 0:
    print('ERROR: no se encontró el bloque JS'); sys.exit(1)

# Find the end: look for the last closing brace of propBuildPDFHTML
# We look for "  return html;\n}\n" after the JS start
js_end_marker = '\n  return html;\n}\n'
js_end = html.find(js_end_marker, js_start)
if js_end < 0:
    print('ERROR: no se encontró el fin del JS'); sys.exit(1)
js_end += len(js_end_marker)

html = html[:js_start] + NEW_JS + html[js_end:]
print('OK JS reemplazado')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'\nListo — {FILE} actualizado ({len(html)} chars)')
