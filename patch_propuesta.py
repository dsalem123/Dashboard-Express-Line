"""
patch_propuesta.py — Agrega módulo "Propuesta de Cartera"
"""
import re, sys

FILE = 'crm_offshore_cambios.html'
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ══════════════════════════════════════════════════════════
# 1. CSS
# ══════════════════════════════════════════════════════════
CSS = """
/* ── PROPUESTA DE CARTERA ── */
#prop-pdf-stage{position:absolute;left:-9999px;top:0;width:794px;background:#0a1f1b;pointer-events:none;}
.prop-layout{display:flex;height:calc(100% - 70px);gap:0;overflow:hidden;}
.prop-sidebar{width:196px;min-width:180px;border-right:1px solid rgba(168,218,187,.1);overflow-y:auto;flex-shrink:0;display:flex;flex-direction:column;}
.prop-sidebar-hdr{display:flex;align-items:center;justify-content:space-between;padding:13px 14px;border-bottom:1px solid rgba(168,218,187,.08);flex-shrink:0;}
.prop-sidebar-hdr span{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--vg);}
.prop-btn-new{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.22);border-radius:5px;color:var(--gold);font-size:10px;padding:4px 10px;cursor:pointer;font-family:Inter,sans-serif;white-space:nowrap;}
.prop-btn-new:hover{background:rgba(201,168,76,.2);}
.prop-list-item{padding:11px 14px;cursor:pointer;border-bottom:1px solid rgba(168,218,187,.05);transition:background .15s;border-left:3px solid transparent;}
.prop-list-item:hover{background:rgba(168,218,187,.04);}
.prop-list-item.active{background:rgba(168,218,187,.06);border-left-color:var(--gold);}
.prop-list-name{font-size:11px;color:var(--cream);font-weight:500;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:154px;}
.prop-list-client{font-size:10px;color:var(--vg);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:154px;}
.prop-main{flex:1;overflow-y:auto;padding:20px 24px;}
.prop-topbar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap;}
.prop-field{background:rgba(13,41,36,.8);border:1px solid rgba(168,218,187,.14);border-radius:6px;color:var(--cream);font-size:12px;padding:8px 12px;font-family:Inter,sans-serif;outline:none;}
.prop-field:focus{border-color:rgba(201,168,76,.4);}
.prop-name-field{flex:1;min-width:160px;}
.prop-btn-pdf{background:var(--gold);border:none;border-radius:6px;color:#0a1f1b;font-size:11px;font-weight:700;padding:8px 16px;cursor:pointer;font-family:Inter,sans-serif;white-space:nowrap;}
.prop-btn-pdf:hover{opacity:.88;}
.prop-btn-del-main{background:rgba(231,76,60,.08);border:1px solid rgba(231,76,60,.18);border-radius:6px;color:rgba(231,76,60,.7);font-size:14px;padding:6px 10px;cursor:pointer;line-height:1;}
.prop-btn-del-main:hover{color:#e74c3c;background:rgba(231,76,60,.14);}
.prop-desc{width:100%;background:rgba(13,41,36,.6);border:1px solid rgba(168,218,187,.11);border-radius:8px;color:var(--cream);font-size:12px;padding:13px 15px;font-family:Inter,sans-serif;resize:vertical;min-height:68px;max-height:160px;outline:none;margin-bottom:18px;line-height:1.6;box-sizing:border-box;}
.prop-desc:focus{border-color:rgba(201,168,76,.3);}
.prop-desc::placeholder{color:var(--vg);}
.prop-body{display:flex;gap:18px;align-items:flex-start;}
.prop-chart-col{width:230px;min-width:200px;flex-shrink:0;}
.prop-section-lbl{font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:10px;}
.prop-chart-wrap{background:rgba(13,41,36,.5);border-radius:8px;padding:16px;text-align:center;}
.prop-legend{margin-top:10px;}
.prop-legend-item{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(168,218,187,.05);}
.prop-legend-dot{width:9px;height:9px;border-radius:2px;flex-shrink:0;}
.prop-legend-name{flex:1;font-size:11px;color:var(--cream);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.prop-legend-pct{font-size:11px;font-weight:700;color:var(--gold);min-width:34px;text-align:right;}
.prop-assets-col{flex:1;min-width:0;}
.prop-assets-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}
.prop-table{width:100%;border-collapse:collapse;}
.prop-table th{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:var(--vg);font-weight:700;padding:7px 8px;border-bottom:2px solid rgba(168,218,187,.1);text-align:left;}
.prop-table th:nth-child(3){text-align:right;width:80px;}
.prop-table th:nth-child(4){width:30px;}
.prop-inp{background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.1);border-radius:4px;color:var(--cream);font-size:11px;padding:5px 8px;font-family:Inter,sans-serif;outline:none;width:100%;box-sizing:border-box;}
.prop-inp:focus{border-color:rgba(201,168,76,.35);}
.prop-pct-inp{width:70px;text-align:right;}
.prop-sel{background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.1);border-radius:4px;color:var(--cream);font-size:11px;padding:5px 6px;font-family:Inter,sans-serif;outline:none;width:100%;}
.prop-asset-row td{padding:5px 6px;border-bottom:1px solid rgba(168,218,187,.04);}
.prop-btn-row-del{background:none;border:none;color:rgba(231,76,60,.4);font-size:17px;cursor:pointer;padding:2px 5px;border-radius:3px;line-height:1;}
.prop-btn-row-del:hover{color:#e74c3c;background:rgba(231,76,60,.1);}
.prop-btn-add{background:rgba(168,218,187,.06);border:1px solid rgba(168,218,187,.14);border-radius:5px;color:var(--mint);font-size:10px;padding:5px 12px;cursor:pointer;font-family:Inter,sans-serif;}
.prop-btn-add:hover{background:rgba(168,218,187,.11);}
.prop-total{padding:10px 8px 4px;text-align:right;}
.prop-empty{padding:40px 20px;text-align:center;color:var(--vg);font-size:12px;}
"""

OLD_STYLE = '</style>'
if CSS.strip()[:30] in html:
    print('CSS ya aplicado — saltando')
elif OLD_STYLE not in html:
    print('ERROR: no se encontró </style>'); sys.exit(1)
else:
    html = html.replace(OLD_STYLE, CSS + OLD_STYLE, 1)
    print('OK CSS agregado')

# ══════════════════════════════════════════════════════════
# 2. NAV item — después de Cartera modelo
# ══════════════════════════════════════════════════════════
NAV_CARTERA = '    <button class="nav-item" onclick="showPage(\'cartera\',this)"><span class="nav-item-icon">💼</span><span class="nav-item-text">Cartera modelo</span></button>'
NAV_NEW = '\n    <button class="nav-item" onclick="showPage(\'propuesta\',this);initPropuesta()"><span class="nav-item-icon">📋</span><span class="nav-item-text">Propuesta de Cartera</span></button>'

if 'showPage(\'propuesta\'' in html:
    print('NAV ya aplicado — saltando')
elif NAV_CARTERA not in html:
    print('ERROR: no se encontró nav Cartera modelo'); sys.exit(1)
else:
    html = html.replace(NAV_CARTERA, NAV_CARTERA + NAV_NEW, 1)
    print('OK NAV agregado')

# ══════════════════════════════════════════════════════════
# 3. HTML de la página — antes de </div><!-- /content-area -->
# ══════════════════════════════════════════════════════════
PAGE_HTML = """
<div id="page-propuesta" class="page" style="display:none;">
  <div class="page-header">
    <div class="header-left">
      <div class="header-title">Propuesta de Cartera</div>
    </div>
    <span class="badge">Propuesta &middot; Offshore</span>
  </div>
  <div class="prop-layout">
    <div class="prop-sidebar">
      <div class="prop-sidebar-hdr">
        <span>Propuestas</span>
        <button class="prop-btn-new" onclick="propNew()">+ Nueva</button>
      </div>
      <div id="prop-list"></div>
    </div>
    <div class="prop-main" id="prop-main">
      <div id="prop-editor">
        <div class="prop-topbar">
          <select id="prop-client-sel" class="prop-field" onchange="propSetClient(this.value)"><option value="">— Cliente —</option></select>
          <input id="prop-name-inp" class="prop-field prop-name-field" type="text" placeholder="Nombre de la propuesta" onblur="propSetName(this.value)">
          <button class="prop-btn-pdf" onclick="propDownloadPDF()">&#11015; PDF</button>
          <button class="prop-btn-del-main" title="Eliminar propuesta" onclick="propDeleteActive()">&#128465;</button>
        </div>
        <textarea id="prop-desc-inp" class="prop-desc" placeholder="Descripción: perfil del inversor, objetivos, horizonte temporal..."></textarea>
        <div class="prop-body">
          <div class="prop-chart-col">
            <div class="prop-section-lbl">Distribución</div>
            <div class="prop-chart-wrap">
              <div id="prop-chart-svg"></div>
            </div>
            <div id="prop-legend" class="prop-legend"></div>
          </div>
          <div class="prop-assets-col">
            <div class="prop-assets-hdr">
              <span class="prop-section-lbl">Activos</span>
              <button class="prop-btn-add" onclick="propAddAsset()">+ Agregar</button>
            </div>
            <table class="prop-table">
              <thead><tr>
                <th>Activo</th><th>Tipo</th><th style="text-align:right;">%</th><th></th>
              </tr></thead>
              <tbody id="prop-assets-body"></tbody>
            </table>
            <div id="prop-total-display" class="prop-total"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div id="prop-pdf-stage"></div>
</div>
"""

OLD_CONTENT_END = '</div><!-- /content-area -->'
if 'page-propuesta' in html:
    print('HTML página ya aplicado — saltando')
elif OLD_CONTENT_END not in html:
    print('ERROR: no se encontró /content-area'); sys.exit(1)
else:
    html = html.replace(OLD_CONTENT_END, PAGE_HTML + OLD_CONTENT_END, 1)
    print('OK HTML página agregado')

# ══════════════════════════════════════════════════════════
# 4. JS — antes del </script> final
# ══════════════════════════════════════════════════════════
JS = """
// ════════════════════════════════════════════════════════
// PROPUESTA DE CARTERA
// ════════════════════════════════════════════════════════
var PROP={proposals:[],activeId:null};
var PROP_COLORS=['#A8DABB','#C9A84C','#5B9BD5','#F59E0B','#8B5CF6','#EF4444','#14B8A6','#F97316','#EC4899','#84CC16'];
var PROP_TIPOS=['Equity','Bonos','Cash','ETF','Fondo','Real Estate','Commodities','Alternativo','Otro'];

function propEsc(s){return s==null?'':String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

function initPropuesta(){
  try{PROP.proposals=JSON.parse(localStorage.getItem('crm_propuestas')||'[]');}catch(e){PROP.proposals=[];}
  propRenderSidebar();
  if(!PROP.proposals.length){propNew(true);return;}
  PROP.activeId=PROP.proposals[0].id;
  propRenderEditor();
}

function propSave(){try{localStorage.setItem('crm_propuestas',JSON.stringify(PROP.proposals));}catch(e){}}

function propActive(){return PROP.proposals.find(function(p){return p.id===PROP.activeId;})||null;}

function propNew(silent){
  var id='prop_'+Date.now();
  PROP.proposals.unshift({id:id,clientName:'',name:'Nueva propuesta',description:'',assets:[]});
  PROP.activeId=id;
  propSave();
  propRenderSidebar();
  propRenderEditor();
}

function propSelect(id){
  PROP.activeId=id;
  propRenderSidebar();
  propRenderEditor();
}

function propDeleteActive(){
  var p=propActive();
  if(!p)return;
  if(!confirm('¿Eliminar "'+p.name+'"?'))return;
  PROP.proposals=PROP.proposals.filter(function(x){return x.id!==p.id;});
  PROP.activeId=PROP.proposals.length?PROP.proposals[0].id:null;
  propSave();
  propRenderSidebar();
  propRenderEditor();
}

function propRenderSidebar(){
  var el=document.getElementById('prop-list');if(!el)return;
  if(!PROP.proposals.length){el.innerHTML='<div class="prop-empty">Sin propuestas</div>';return;}
  el.innerHTML=PROP.proposals.map(function(p){
    return '<div class="prop-list-item'+(p.id===PROP.activeId?' active':'')+'" onclick="propSelect(\''+propEsc(p.id)+'\')">'+
      '<div class="prop-list-name">'+propEsc(p.name)+'</div>'+
      '<div class="prop-list-client">'+propEsc(p.clientName||'Sin cliente')+'</div>'+
    '</div>';
  }).join('');
}

function propRenderEditor(){
  var p=propActive();
  var clients=[];try{clients=JSON.parse(localStorage.getItem('crm_clients')||'[]');}catch(e){}
  var sel=document.getElementById('prop-client-sel');
  if(sel){
    sel.innerHTML='<option value="">— Cliente —</option>'+
      clients.map(function(c){return '<option value="'+propEsc(c.nombre)+'"'+(p&&c.nombre===p.clientName?' selected':'')+'>'+propEsc(c.nombre)+'</option>';}).join('');
  }
  var ni=document.getElementById('prop-name-inp');if(ni)ni.value=p?p.name:'';
  var di=document.getElementById('prop-desc-inp');
  if(di){
    di.value=p?p.description:'';
    di.oninput=function(){var pp=propActive();if(pp){pp.description=this.value;propSave();}};
  }
  propRenderAssets();
  propRenderChart();
}

function propRenderAssets(){
  var p=propActive();if(!p)return;
  var tb=document.getElementById('prop-assets-body');if(!tb)return;
  tb.innerHTML=p.assets.map(function(a,i){
    var opts=PROP_TIPOS.map(function(t){return '<option'+(t===a.tipo?' selected':'')+'>'+t+'</option>';}).join('');
    return '<tr class="prop-asset-row">'+
      '<td><input class="prop-inp" type="text" value="'+propEsc(a.name||'')+'" placeholder="Nombre del activo"'+
        ' data-idx="'+i+'" onchange="propUpdateAsset('+i+',\'name\',this.value)"></td>'+
      '<td><select class="prop-sel" data-idx="'+i+'" onchange="propUpdateAsset('+i+',\'tipo\',this.value)">'+opts+'</select></td>'+
      '<td><input class="prop-inp prop-pct-inp" type="number" min="0" max="100" step="0.1" value="'+propEsc(String(a.pct||''))+'"'+
        ' placeholder="0" data-idx="'+i+'" onchange="propUpdateAsset('+i+',\'pct\',this.value)"></td>'+
      '<td><button class="prop-btn-row-del" onclick="propRemoveAsset('+i+')">&times;</button></td>'+
    '</tr>';
  }).join('');
  var total=p.assets.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
  var ok=Math.abs(total-100)<0.01, over=total>100;
  var col=ok?'#2ecc71':over?'#e74c3c':'#C9A84C';
  var td=document.getElementById('prop-total-display');
  if(td)td.innerHTML='<span style="font-size:10px;letter-spacing:1px;text-transform:uppercase;color:#6B8578;">Total</span>'+
    '<span style="font-size:20px;font-weight:700;color:'+col+';font-family:\'Playfair Display\',serif;margin-left:10px;">'+total.toFixed(1)+'%</span>'+
    (ok?'':over?'<span style="font-size:10px;color:'+col+';margin-left:8px;">excede 100%</span>':
      '<span style="font-size:10px;color:'+col+';margin-left:8px;">faltan '+(100-total).toFixed(1)+'%</span>');
}

function propUpdateAsset(idx,field,val){
  var p=propActive();if(!p)return;
  p.assets[idx][field]=field==='pct'?parseFloat(val)||0:val;
  propSave();
  propRenderChart();
  propRenderAssets();
}

function propAddAsset(){
  var p=propActive();if(!p)return;
  p.assets.push({name:'',tipo:'Equity',pct:0});
  propSave();
  propRenderAssets();
  propRenderChart();
  // Focus the new name input
  setTimeout(function(){
    var rows=document.querySelectorAll('.prop-asset-row');
    if(rows.length){var inp=rows[rows.length-1].querySelector('.prop-inp');if(inp)inp.focus();}
  },50);
}

function propRemoveAsset(idx){
  var p=propActive();if(!p)return;
  p.assets.splice(idx,1);
  propSave();
  propRenderAssets();
  propRenderChart();
}

function propSetClient(val){var p=propActive();if(!p)return;p.clientName=val;propSave();propRenderSidebar();}
function propSetName(val){var p=propActive();if(!p)return;p.name=val||'Sin nombre';propSave();propRenderSidebar();}

function propBuildSVG(assets,size){
  size=size||240;
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
  var fs=(size*0.09).toFixed(0),fs2=(size*0.038).toFixed(0);
  return '<svg width="'+size+'" height="'+size+'" viewBox="0 0 '+size+' '+size+'">'+
    paths+
    '<circle cx="'+cx+'" cy="'+cy+'" r="'+(ri-1)+'" fill="#0a1f1b"/>'+
    '<text x="'+cx+'" y="'+(cy-6)+'" text-anchor="middle" fill="#ECEDE3" font-size="'+fs+'" font-weight="700" font-family="\'Playfair Display\',serif">'+total.toFixed(1)+'%</text>'+
    '<text x="'+cx+'" y="'+(cy+12)+'" text-anchor="middle" fill="#6B8578" font-size="'+fs2+'" font-family="Inter,sans-serif" letter-spacing="1.5">TOTAL</text>'+
    '</svg>';
}

function propRenderChart(){
  var p=propActive();if(!p)return;
  var el=document.getElementById('prop-chart-svg');if(!el)return;
  el.innerHTML=propBuildSVG(p.assets,200);
  var leg=document.getElementById('prop-legend');if(!leg)return;
  var valid=p.assets.filter(function(a){return (parseFloat(a.pct)||0)>0;});
  if(!valid.length){leg.innerHTML='';return;}
  leg.innerHTML=valid.map(function(a,i){
    return '<div class="prop-legend-item">'+
      '<div class="prop-legend-dot" style="background:'+PROP_COLORS[i%PROP_COLORS.length]+';"></div>'+
      '<div class="prop-legend-name">'+propEsc(a.name||'Sin nombre')+'</div>'+
      '<div class="prop-legend-pct">'+a.pct+'%</div>'+
    '</div>';
  }).join('');
}

function propDownloadPDF(){
  var p=propActive();if(!p){showToast('No hay propuesta activa',true);return;}
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
      doc.save('Propuesta_'+propEsc((p.clientName||'cliente').replace(/[^a-zA-Z0-9]/g,'_'))+'_'+new Date().toISOString().split('T')[0]+'.pdf');
      stage.innerHTML='';showToast('PDF descargado');
    }).catch(function(e){showToast('Error al generar PDF',true);stage.innerHTML='';console.error(e);});
  },300);
}

function propBuildPDFHTML(p){
  var BG='#0a1f1b',CARD='#0e2822',BORDER='#1d3a35',GOLD='#C9A84C',MINT='#A8DABB',CREAM='#ECEDE3',MUTED='#6B8578';
  var today=new Date().toLocaleDateString('es-AR',{day:'2-digit',month:'long',year:'numeric'});
  var valid=p.assets.filter(function(a){return (parseFloat(a.pct)||0)>0;});
  var total=valid.reduce(function(s,a){return s+(parseFloat(a.pct)||0);},0);
  var svgChart=propBuildSVG(valid,260);
  var thS='padding:8px 8px;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:'+MUTED+';font-weight:700;border-bottom:2px solid '+BORDER+';';
  var rowsHTML=valid.map(function(a,i){
    return '<tr>'+
      '<td style="padding:8px;"><div style="width:10px;height:10px;border-radius:2px;background:'+PROP_COLORS[i%PROP_COLORS.length]+';"></div></td>'+
      '<td style="padding:8px;font-size:11px;color:'+CREAM+';">'+propEsc(a.name)+'</td>'+
      '<td style="padding:8px;font-size:10px;color:'+MUTED+';text-align:center;">'+propEsc(a.tipo)+'</td>'+
      '<td style="padding:8px;font-size:14px;font-weight:700;color:'+CREAM+';text-align:right;font-family:\'Playfair Display\',serif;">'+a.pct+'%</td>'+
    '</tr>';
  }).join('');

  var html='<div style="background:'+BG+';padding:44px 48px 40px;font-family:Inter,sans-serif;color:'+CREAM+';width:794px;box-sizing:border-box;line-height:1.4;">';

  // Header
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

  // Client + name
  html+='<div style="margin-bottom:22px;">'+
    '<div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:'+MUTED+';margin-bottom:6px;">Cliente</div>'+
    '<div style="font-family:\'Playfair Display\',serif;font-size:28px;color:'+CREAM+';font-weight:600;line-height:1.15;">'+(p.clientName||'—').toUpperCase()+'</div>'+
    '<div style="font-size:13px;color:'+GOLD+';margin-top:6px;letter-spacing:.5px;">'+propEsc(p.name)+'</div>'+
    '<div style="width:50px;height:2px;background:'+GOLD+';margin-top:10px;"></div>'+
  '</div>';

  // Description
  if(p.description){
    html+='<div style="background:'+CARD+';border-radius:8px;padding:18px 22px;margin-bottom:20px;">'+
      '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:10px;">Descripción</div>'+
      '<div style="font-size:12px;color:'+CREAM+';line-height:1.8;">'+propEsc(p.description).replace(/\n/g,'<br>')+'</div>'+
    '</div>';
  }

  // Chart + composition table
  html+='<table width="100%" cellpadding="0" cellspacing="0"><tr>'+
    '<td width="44%" style="vertical-align:top;background:'+BG+';padding-right:16px;">'+
      '<div style="background:'+CARD+';border-radius:8px;padding:20px;text-align:center;">'+
        '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid '+BORDER+';">Distribución</div>'+
        svgChart+
      '</div>'+
    '</td>'+
    '<td width="56%" style="vertical-align:top;background:'+BG+';">'+
      '<div style="background:'+CARD+';border-radius:8px;padding:20px;">'+
        '<div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:'+GOLD+';margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid '+BORDER+';">Composición</div>'+
        '<table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">'+
          '<thead><tr>'+
            '<th style="'+thS+'width:16px;"></th>'+
            '<th style="'+thS+'text-align:left;">Activo</th>'+
            '<th style="'+thS+'text-align:center;">Tipo</th>'+
            '<th style="'+thS+'text-align:right;">%</th>'+
          '</tr></thead>'+
          '<tbody>'+rowsHTML+'</tbody>'+
          '<tfoot><tr>'+
            '<td colspan="3" style="padding:10px 8px;border-top:1px solid '+BORDER+';font-size:9px;letter-spacing:1px;text-transform:uppercase;color:'+GOLD+';font-weight:700;">Total</td>'+
            '<td style="padding:10px 8px;border-top:1px solid '+BORDER+';text-align:right;font-size:16px;font-weight:700;color:'+GOLD+';font-family:\'Playfair Display\',serif;">'+total.toFixed(1)+'%</td>'+
          '</tr></tfoot>'+
        '</table>'+
      '</div>'+
    '</td>'+
  '</tr></table>';

  // Footer
  html+='<div style="height:1px;background:'+BORDER+';margin-top:24px;margin-bottom:14px;"></div>'+
  '<table width="100%" cellpadding="0" cellspacing="0"><tr>'+
    '<td style="font-size:9px;color:#3a5a52;letter-spacing:1.5px;text-transform:uppercase;background:'+BG+';">Express Line &middot; Propuesta Confidencial</td>'+
    '<td style="text-align:right;font-size:9px;color:#3a5a52;background:'+BG+';">Generado el '+today+'</td>'+
  '</tr></table></div>';

  return html;
}
"""

LAST_SCRIPT = '</script>\n</body>'
if 'function initPropuesta' in html:
    print('JS ya aplicado — saltando')
elif LAST_SCRIPT not in html:
    print('ERROR: no se encontró </script> final'); sys.exit(1)
else:
    html = html.replace(LAST_SCRIPT, JS + '\n' + LAST_SCRIPT, 1)
    print('OK JS agregado')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nListo — {FILE}: {original_len} -> {len(html)} chars (+{len(html)-original_len})')
