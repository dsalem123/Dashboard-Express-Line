"""
patch_reuniones.py — Agrega modulo Reuniones al CRM OFFSHORE
4 inserciones: CSS, nav item, HTML (pagina + modal), JS completo
"""
import sys, re

FILE = 'crm_offshore_cambios.html'
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()
original = html

# ══════════════════════════════════════════════════════════════
# PASO 1 — CSS (antes de </style>)
# ══════════════════════════════════════════════════════════════
CSS = """
/* ═══════════ REUNIONES MODULE ═══════════ */
.reu-layout{display:grid;grid-template-columns:280px 1fr;gap:24px;padding:24px;height:calc(100vh - 120px);overflow:hidden;}
.reu-clients-panel{background:rgba(13,41,36,.6);border:1px solid rgba(168,218,187,.12);border-radius:12px;overflow:hidden;display:flex;flex-direction:column;}
.reu-panel-title{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;padding:18px 18px 10px;border-bottom:1px solid rgba(168,218,187,.08);}
.reu-clients-list{flex:1;overflow-y:auto;padding:4px 0;}
.reu-client-row{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid rgba(168,218,187,.05);transition:background .15s;}
.reu-client-row:hover{background:rgba(168,218,187,.05);}
.reu-client-info{flex:1;min-width:0;margin-right:8px;}
.reu-client-name{font-size:12px;font-weight:600;color:var(--cream);letter-spacing:.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.reu-client-cnt{font-size:10px;color:var(--gold);margin-top:2px;letter-spacing:.5px;}
.reu-btn-crear{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.25);color:#C9A84C;border-radius:6px;padding:5px 10px;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;cursor:pointer;white-space:nowrap;transition:all .15s;flex-shrink:0;}
.reu-btn-crear:hover{background:rgba(201,168,76,.2);}
.reu-right-panel{display:grid;grid-template-rows:auto 1fr;gap:24px;overflow:hidden;min-height:0;}
.reu-cal-panel{background:rgba(13,41,36,.6);border:1px solid rgba(168,218,187,.12);border-radius:12px;padding:20px 24px;}
.reu-cal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;}
.reu-cal-nav{background:none;border:1px solid rgba(168,218,187,.15);color:var(--cream);border-radius:6px;width:30px;height:30px;cursor:pointer;font-size:20px;line-height:1;transition:all .15s;display:flex;align-items:center;justify-content:center;}
.reu-cal-nav:hover{background:rgba(168,218,187,.1);border-color:rgba(168,218,187,.3);}
.reu-cal-month{font-family:'Playfair Display',serif;font-size:16px;color:var(--cream);font-weight:600;}
.reu-cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;}
.reu-cal-dayname{font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#6B8578;text-align:center;padding:4px 0 8px;}
.reu-cal-empty{min-height:38px;}
.reu-cal-day{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:38px;border-radius:7px;cursor:pointer;transition:background .15s;font-size:12px;color:rgba(236,237,227,.65);position:relative;}
.reu-cal-day:hover{background:rgba(168,218,187,.08);}
.reu-cal-day.today span{background:rgba(201,168,76,.18);color:#C9A84C;font-weight:700;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;}
.reu-cal-day.has-meeting{color:var(--cream);font-weight:600;}
.reu-cal-dot{width:5px;height:5px;background:#A8DABB;border-radius:50%;margin-top:2px;}
.reu-upcoming-panel{background:rgba(13,41,36,.6);border:1px solid rgba(168,218,187,.12);border-radius:12px;padding:16px 20px;overflow-y:auto;min-height:0;}
.reu-section-title{font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:10px;}
.reu-meeting-card{border:1px solid rgba(168,218,187,.1);border-radius:9px;padding:12px 14px;margin-bottom:8px;background:rgba(0,0,0,.15);transition:border-color .15s;}
.reu-meeting-card:hover{border-color:rgba(168,218,187,.22);}
.reu-meeting-card.past{opacity:.5;}
.reu-meeting-client{font-size:13px;font-weight:600;color:var(--cream);}
.reu-meeting-date{font-size:11px;color:#A8DABB;margin-top:2px;}
.reu-meeting-agenda{font-size:11px;color:#6B8578;margin-top:4px;font-style:italic;line-height:1.5;}
.reu-meeting-actions{display:flex;gap:6px;margin-top:10px;}
.reu-btn-pdf{background:rgba(168,218,187,.08);border:1px solid rgba(168,218,187,.18);color:#A8DABB;border-radius:6px;padding:5px 12px;font-size:10px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;cursor:pointer;transition:all .15s;}
.reu-btn-pdf:hover{background:rgba(168,218,187,.16);}
.reu-btn-del{background:none;border:1px solid rgba(197,48,48,.2);color:#C53030;border-radius:6px;width:28px;height:28px;font-size:13px;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;}
.reu-btn-del:hover{background:rgba(197,48,48,.15);}
.reu-modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.72);display:none;align-items:center;justify-content:center;z-index:3000;backdrop-filter:blur(4px);}
.reu-modal-bg.open{display:flex;}
.reu-modal{background:#0e2219;border:1px solid rgba(168,218,187,.2);border-radius:14px;width:440px;max-width:95vw;overflow:hidden;box-shadow:0 24px 64px rgba(0,0,0,.6);}
.reu-modal-header{padding:24px 24px 16px;border-bottom:1px solid rgba(168,218,187,.1);}
.reu-modal-title{font-family:'Playfair Display',serif;font-size:20px;color:var(--cream);font-weight:600;}
.reu-modal-clientlbl{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#C9A84C;margin-top:4px;}
.reu-modal-body{padding:20px 24px;display:flex;flex-direction:column;gap:14px;}
.reu-field label{display:block;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#6B8578;margin-bottom:5px;}
.reu-field input,.reu-field textarea{width:100%;background:rgba(0,0,0,.3);border:1px solid rgba(168,218,187,.18);border-radius:7px;padding:9px 12px;font-size:13px;color:var(--cream);font-family:'Inter',sans-serif;outline:none;transition:border-color .15s;box-sizing:border-box;}
.reu-field input:focus,.reu-field textarea:focus{border-color:rgba(201,168,76,.45);}
.reu-field textarea{resize:vertical;min-height:70px;line-height:1.5;}
.reu-row-fields{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.reu-modal-footer{padding:14px 24px 20px;display:flex;gap:10px;justify-content:flex-end;border-top:1px solid rgba(168,218,187,.08);}
.reu-btn-cancel{background:none;border:1px solid rgba(168,218,187,.15);color:#6B8578;border-radius:7px;padding:9px 20px;font-size:12px;font-weight:600;letter-spacing:.5px;cursor:pointer;transition:all .15s;}
.reu-btn-cancel:hover{color:var(--cream);border-color:rgba(168,218,187,.3);}
.reu-btn-save{background:#C9A84C;border:none;color:#0a1f1b;border-radius:7px;padding:9px 22px;font-size:12px;font-weight:700;letter-spacing:.5px;cursor:pointer;transition:opacity .15s;}
.reu-btn-save:hover{opacity:.85;}
#reu-pdf-stage{position:fixed;left:-9999px;top:0;width:794px;background:#0a1f1b;pointer-events:none;z-index:-1;}
"""

OLD_STYLE_END = '.mkt-hg-bear{font-size:9px;font-weight:700;letter-spacing:.5px;padding:2px 7px;border-radius:3px;background:rgba(231,76,60,.12);color:#e74c3c;border:1px solid rgba(231,76,60,.25);margin-left:7px;vertical-align:middle;white-space:nowrap;}\n\n</style>'
NEW_STYLE_END = OLD_STYLE_END.replace('\n\n</style>', CSS + '\n</style>')

if 'reu-layout' in html:
    print('Paso 1 ya aplicado — saltando CSS')
elif OLD_STYLE_END not in html:
    print('ERROR: no se encontro el ancla del </style>')
    sys.exit(1)
else:
    html = html.replace(OLD_STYLE_END, NEW_STYLE_END, 1)
    print('OK Paso 1: CSS agregado')

# ══════════════════════════════════════════════════════════════
# PASO 2 — Nav item
# ══════════════════════════════════════════════════════════════
OLD_NAV = "    <button class=\"nav-item\" onclick=\"showPage('links',this)\"><span class=\"nav-item-icon\">🔗</span><span class=\"nav-item-text\">Links útiles</span></button>\n  </nav>"
NEW_NAV = OLD_NAV.replace(
    '  </nav>',
    '    <button class="nav-item" onclick="showPage(\'reuniones\',this);initReuniones()"><span class="nav-item-icon">📅</span><span class="nav-item-text">Reuniones</span></button>\n  </nav>'
)

if 'initReuniones' in html:
    print('Paso 2 ya aplicado — saltando nav')
elif OLD_NAV not in html:
    print('ERROR: no se encontro el nav item de Links utiles')
    sys.exit(1)
else:
    html = html.replace(OLD_NAV, NEW_NAV, 1)
    print('OK Paso 2: nav item agregado')

# ══════════════════════════════════════════════════════════════
# PASO 3 — HTML: pagina + modal (antes de </div><!-- /content-area -->)
# ══════════════════════════════════════════════════════════════
PAGE_HTML = """
<div id="page-reuniones" class="page">
  <div class="doc-header">
    <div>
      <div class="logo-wordmark">ExpressLine</div>
      <div class="header-title">Reuniones</div>
      <div class="gold-line"></div>
      <div class="header-sub">Offshore &middot; Gesti&oacute;n de reuniones con clientes</div>
    </div>
  </div>
  <div class="reu-layout">
    <div class="reu-clients-panel">
      <div class="reu-panel-title">Clientes</div>
      <div class="reu-clients-list" id="reu-clients-list"></div>
    </div>
    <div class="reu-right-panel">
      <div class="reu-cal-panel" id="reu-cal"></div>
      <div class="reu-upcoming-panel" id="reu-upcoming"></div>
    </div>
  </div>
</div>
"""

OLD_CONTENT_END = '\n</div><!-- /content-area -->'
NEW_CONTENT_END = PAGE_HTML + OLD_CONTENT_END

if 'page-reuniones' in html:
    print('Paso 3 ya aplicado — saltando HTML pagina')
elif OLD_CONTENT_END not in html:
    print('ERROR: no se encontro </div><!-- /content-area -->')
    sys.exit(1)
else:
    html = html.replace(OLD_CONTENT_END, NEW_CONTENT_END, 1)
    print('OK Paso 3: pagina HTML agregada')

# Modal (antes del primer modal existente)
MODAL_HTML = '\n<div class="reu-modal-bg" id="reu-modal-bg" onclick="if(event.target===this)reuCloseModal()">\n  <div class="reu-modal" id="reu-modal"></div>\n</div>\n'
OLD_MODAL_ANCHOR = '\n<div class="mgr-drawer">'
NEW_MODAL_ANCHOR = MODAL_HTML + OLD_MODAL_ANCHOR

if 'reu-modal-bg' in html:
    print('Paso 3b ya aplicado — saltando modal HTML')
elif OLD_MODAL_ANCHOR not in html:
    print('ERROR: no se encontro el ancla del mgr-drawer')
    sys.exit(1)
else:
    html = html.replace(OLD_MODAL_ANCHOR, NEW_MODAL_ANCHOR, 1)
    print('OK Paso 3b: modal HTML agregado')

# ══════════════════════════════════════════════════════════════
# PASO 4 — JS: modulo completo antes de </script> final
# ══════════════════════════════════════════════════════════════
JS = r"""

// ════════════════════════════════════════════════════════════
// REUNIONES MODULE
// ════════════════════════════════════════════════════════════
var REU={meetings:[],calYear:0,calMonth:0};

function reuEsc(s){if(s==null)return '';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

function initReuniones(){
  try{REU.meetings=JSON.parse(localStorage.getItem('crm_reuniones')||'[]');}catch(e){REU.meetings=[];}
  var now=new Date(); REU.calYear=now.getFullYear(); REU.calMonth=now.getMonth();
  reuRender();
}

function reuSave(){try{localStorage.setItem('crm_reuniones',JSON.stringify(REU.meetings));}catch(e){}}

function reuRender(){reuRenderClients();reuRenderCal();reuRenderUpcoming();}

function reuRenderClients(){
  var clients=[]; try{clients=JSON.parse(localStorage.getItem('crm_clients')||'[]');}catch(e){}
  var el=document.getElementById('reu-clients-list'); if(!el) return;
  if(!clients.length){el.innerHTML='<div style="padding:24px;color:#6B8578;font-size:12px;text-align:center;">Sin clientes</div>';return;}
  var h='';
  clients.forEach(function(c){
    var name=c.nombre||'—';
    var cnt=REU.meetings.filter(function(m){return String(m.clientId)===String(c.id);}).length;
    h+='<div class="reu-client-row"><div class="reu-client-info"><div class="reu-client-name">'+reuEsc(name)+'</div>';
    if(cnt>0) h+='<div class="reu-client-cnt">'+cnt+' reunión'+(cnt>1?'es':'')+'</div>';
    h+='</div><button class="reu-btn-crear" onclick="reuOpenModal('+JSON.stringify(c.id)+','+JSON.stringify(name)+')">+ Crear</button></div>';
  });
  el.innerHTML=h;
}

function reuRenderCal(){
  var el=document.getElementById('reu-cal'); if(!el) return;
  var year=REU.calYear,month=REU.calMonth;
  var mn=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
  var dn=['L','M','X','J','V','S','D'];
  var mtgs={};
  REU.meetings.forEach(function(m){
    var d=new Date(m.date+'T12:00:00');
    if(d.getFullYear()===year&&d.getMonth()===month){var day=d.getDate();if(!mtgs[day])mtgs[day]=[];mtgs[day].push(m);}
  });
  var firstDay=new Date(year,month,1).getDay(); firstDay=firstDay===0?6:firstDay-1;
  var dim=new Date(year,month+1,0).getDate();
  var today=new Date(); var todayD=(today.getFullYear()===year&&today.getMonth()===month)?today.getDate():-1;
  var h='<div class="reu-cal-header"><button class="reu-cal-nav" onclick="reuCalPrev()">&#8249;</button><span class="reu-cal-month">'+mn[month]+' '+year+'</span><button class="reu-cal-nav" onclick="reuCalNext()">&#8250;</button></div><div class="reu-cal-grid">';
  dn.forEach(function(d){h+='<div class="reu-cal-dayname">'+d+'</div>';});
  for(var i=0;i<firstDay;i++) h+='<div class="reu-cal-empty"></div>';
  for(var d=1;d<=dim;d++){
    var cls='reu-cal-day'+(d===todayD?' today':'')+(mtgs[d]?' has-meeting':'');
    h+='<div class="'+cls+'"><span>'+d+'</span>'+(mtgs[d]?'<div class="reu-cal-dot"></div>':'')+'</div>';
  }
  h+='</div>';
  el.innerHTML=h;
}

function reuRenderUpcoming(){
  var el=document.getElementById('reu-upcoming'); if(!el) return;
  var todayStr=new Date().toISOString().slice(0,10);
  var sorted=REU.meetings.slice().sort(function(a,b){return(a.date+a.time)<(b.date+b.time)?-1:1;});
  var upcoming=sorted.filter(function(m){return m.date>=todayStr;});
  var past=sorted.filter(function(m){return m.date<todayStr;}).reverse().slice(0,5);
  var h='';
  if(upcoming.length){h+='<div class="reu-section-title">Próximas</div>';upcoming.forEach(function(m){h+=reuCard(m,false);});}
  if(past.length){h+='<div class="reu-section-title" style="margin-top:18px;">Recientes</div>';past.forEach(function(m){h+=reuCard(m,true);});}
  if(!upcoming.length&&!past.length) h='<div style="padding:28px;text-align:center;color:#6B8578;font-size:12px;">Sin reuniones agendadas.<br>Creá una desde la lista de clientes.</div>';
  el.innerHTML=h;
}

function reuCard(m,isPast){
  var d=new Date(m.date+'T12:00:00');
  var dn=['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];
  var mn2=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  var ds=dn[d.getDay()]+' '+d.getDate()+' '+mn2[d.getMonth()];
  var h='<div class="reu-meeting-card'+(isPast?' past':'')+'"><div class="reu-meeting-client">'+reuEsc(m.clientName)+'</div>';
  h+='<div class="reu-meeting-date">'+ds+(m.time?' &middot; '+m.time:'')+'</div>';
  if(m.agenda) h+='<div class="reu-meeting-agenda">'+reuEsc(m.agenda)+'</div>';
  h+='<div class="reu-meeting-actions"><button class="reu-btn-pdf" onclick="reuGeneratePDF('+JSON.stringify(m.id)+')">&#128196;&nbsp;Generar informe</button><button class="reu-btn-del" title="Eliminar" onclick="reuDeleteMeeting('+JSON.stringify(m.id)+')">&#10005;</button></div></div>';
  return h;
}

function reuCalPrev(){REU.calMonth--;if(REU.calMonth<0){REU.calMonth=11;REU.calYear--;}reuRenderCal();}
function reuCalNext(){REU.calMonth++;if(REU.calMonth>11){REU.calMonth=0;REU.calYear++;}reuRenderCal();}

function reuOpenModal(clientId,clientName){
  var modal=document.getElementById('reu-modal'),bg=document.getElementById('reu-modal-bg');
  if(!modal||!bg) return;
  var today=new Date().toISOString().slice(0,10);
  modal.innerHTML=
    '<div class="reu-modal-header"><div class="reu-modal-title">Nueva reunión</div><div class="reu-modal-clientlbl">'+reuEsc(clientName)+'</div></div>'+
    '<div class="reu-modal-body">'+
      '<div class="reu-row-fields"><div class="reu-field"><label>Fecha</label><input type="date" id="reu-inp-date" value="'+today+'"></div>'+
      '<div class="reu-field"><label>Hora</label><input type="time" id="reu-inp-time" value="10:00"></div></div>'+
      '<div class="reu-field"><label>Agenda / Notas</label><textarea id="reu-inp-agenda" placeholder="Temas a tratar, observaciones previas..."></textarea></div>'+
    '</div>'+
    '<div class="reu-modal-footer"><button class="reu-btn-cancel" onclick="reuCloseModal()">Cancelar</button>'+
    '<button class="reu-btn-save" onclick="reuSaveMeeting('+JSON.stringify(clientId)+','+JSON.stringify(clientName)+')">Agendar reunión</button></div>';
  bg.classList.add('open');
}

function reuCloseModal(){var bg=document.getElementById('reu-modal-bg');if(bg)bg.classList.remove('open');}

function reuSaveMeeting(clientId,clientName){
  var de=document.getElementById('reu-inp-date'),te=document.getElementById('reu-inp-time'),ae=document.getElementById('reu-inp-agenda');
  if(!de||!de.value){alert('Seleccioná una fecha');return;}
  var m={id:'r_'+Date.now(),clientId:clientId,clientName:clientName,date:de.value,time:te?te.value:'',agenda:ae?ae.value.trim():'',createdAt:new Date().toISOString()};
  REU.meetings.push(m); reuSave(); reuCloseModal(); reuRender();
  showToast('Reunión agendada con '+clientName);
}

function reuDeleteMeeting(id){
  if(!confirm('¿Eliminar esta reunión?')) return;
  REU.meetings=REU.meetings.filter(function(m){return m.id!==id;}); reuSave(); reuRender();
}

function reuGeneratePDF(meetingId){
  var meeting=REU.meetings.find(function(m){return m.id===meetingId;});
  if(!meeting){showToast('Reunión no encontrada',true);return;}
  var clients=[]; try{clients=JSON.parse(localStorage.getItem('crm_clients')||'[]');}catch(e){}
  var client=clients.find(function(c){return String(c.id)===String(meeting.clientId);})||{};
  var pfolData={}; try{pfolData=JSON.parse(localStorage.getItem('pfol_v1')||'{}');}catch(e){}
  var pfolClient=(pfolData.clients||[]).find(function(c){return c.name===(client.nombre||meeting.clientName);})||{};
  var holdings=pfolClient.holdings||[];
  var hgSig={bull:{},bear:{}};
  try{var hgRaw=window._hedgeyeData||JSON.parse(localStorage.getItem('hg_data')||'null');if(hgRaw&&hgRaw.macro_show){(hgRaw.macro_show.bullish||[]).forEach(function(s){hgSig.bull[s.toUpperCase()]=true;});(hgRaw.macro_show.bearish||[]).forEach(function(s){hgSig.bear[s.toUpperCase()]=true;});}}catch(e){}
  var notes=[]; try{notes=JSON.parse(localStorage.getItem('crm_act_'+meeting.clientId)||'[]');}catch(e){}
  var stage=document.getElementById('reu-pdf-stage');
  if(!stage){stage=document.createElement('div');stage.id='reu-pdf-stage';document.body.appendChild(stage);}
  stage.innerHTML=reuBuildPDFHTML(meeting,client,holdings,hgSig,notes);
  showToast('Generando informe...');
  setTimeout(function(){
    html2canvas(stage,{scale:2,backgroundColor:'#0a1f1b',useCORS:true,logging:false,width:794,scrollX:0,scrollY:0})
    .then(function(canvas){
      var doc=new jspdf.jsPDF('p','mm','a4');
      var pw=doc.internal.pageSize.getWidth(),ph=doc.internal.pageSize.getHeight();
      var pxpm=canvas.width/pw, pageHpx=Math.floor(ph*pxpm);
      var npages=Math.ceil(canvas.height/pageHpx);
      for(var pg=0;pg<npages;pg++){
        if(pg>0) doc.addPage();
        var srcY=pg*pageHpx,srcH=Math.min(pageHpx,canvas.height-srcY);
        var pc=document.createElement('canvas'); pc.width=canvas.width; pc.height=pageHpx;
        var ctx=pc.getContext('2d'); ctx.fillStyle='#0a1f1b'; ctx.fillRect(0,0,pc.width,pc.height);
        ctx.drawImage(canvas,0,srcY,canvas.width,srcH,0,0,canvas.width,srcH);
        doc.addImage(pc.toDataURL('image/png'),'PNG',0,0,pw,ph);
      }
      var cn=(client.nombre||meeting.clientName||'cliente').replace(/[\s\/\\]+/g,'_').replace(/[^a-zA-Z0-9_.-]/g,'');
      doc.save('Reunion_'+cn+'_'+meeting.date+'.pdf');
      stage.innerHTML=''; showToast('Informe descargado');
    }).catch(function(e){showToast('Error al generar PDF',true);stage.innerHTML='';console.error(e);});
  },150);
}

function reuBuildPDFHTML(meeting,client,holdings,hgSig,notes){
  var dateObj=new Date(meeting.date+'T12:00:00');
  var months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
  var wdays=['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
  var mds=wdays[dateObj.getDay()]+' '+dateObj.getDate()+' de '+months[dateObj.getMonth()]+' de '+dateObj.getFullYear();
  var todayStr=new Date().toLocaleDateString('es-AR',{day:'2-digit',month:'long',year:'numeric'});
  var cname=(client.nombre||meeting.clientName||'—').toUpperCase();
  var pfields=[['Comitente',client.comitente],['Broker',client.broker],['Custodio',client.custodio],['Tipo de fee',client.tipoFee],['Fee %',client.pctFee],['Perfil de riesgo',client.riesgo],['Plazo',client.plazo],['Seguimiento',client.seguimiento],['Último contacto',client.ultimoContacto],['Comercial',client.comercial]];
  var profHTML=pfields.filter(function(r){return r[1];}).map(function(r){
    return '<tr><td style="padding:5px 0;font-size:10px;color:#6B8578;width:130px;vertical-align:top;">'+reuEsc(r[0])+'</td><td style="padding:5px 0 5px 8px;font-size:11px;color:#ECEDE3;font-weight:500;">'+reuEsc(String(r[1]))+'</td></tr>';
  }).join('');
  var totMV=0,totCost=0,hasCost=false;
  holdings.forEach(function(h){totMV+=parseFloat(h.marketValue)||0;if(h.totalCost!=null){totCost+=parseFloat(h.totalCost)||0;hasCost=true;}});
  var totGain=hasCost?totMV-totCost:null;
  var totGainPct=(hasCost&&totCost>0)?totGain/totCost*100:null;
  var gainColor=totGain!=null?(totGain>=0?'#2ecc71':'#e74c3c'):'#ECEDE3';
  function fmt(v,dec){return v!=null?parseFloat(v).toLocaleString('en-US',{minimumFractionDigits:dec||2,maximumFractionDigits:dec||2}):'—';}
  function fmtMV(v){return v>0?'$'+fmt(v):'—';}
  function fmtGP(v){if(v==null)return '—';return (v>=0?'+':'')+'$'+Math.abs(v).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
  function fmtPct(v){if(v==null)return '—';return (v>=0?'+':'')+parseFloat(v).toFixed(2)+'%';}
  var holdRows='';
  if(holdings.length){
    holdings.forEach(function(h,i){
      var sym=(h.symbol||h.cusip||h.isin||'—').toUpperCase().replace(/^\^/,'');
      var gColor=(h.unrealizedGain!=null)?(parseFloat(h.unrealizedGain)>=0?'#2ecc71':'#e74c3c'):'#ECEDE3';
      var hgB='';
      if(hgSig.bull[sym]) hgB='<span style="font-size:8px;padding:2px 5px;border-radius:3px;background:rgba(46,204,113,.15);color:#2ecc71;border:1px solid rgba(46,204,113,.3);font-weight:700;">&#9650; BULL</span>';
      else if(hgSig.bear[sym]) hgB='<span style="font-size:8px;padding:2px 5px;border-radius:3px;background:rgba(231,76,60,.15);color:#e74c3c;border:1px solid rgba(231,76,60,.3);font-weight:700;">&#9660; BEAR</span>';
      holdRows+='<tr style="background:'+(i%2===0?'rgba(0,0,0,.2)':'transparent')+'">'+
        '<td style="padding:7px 8px;font-size:11px;font-weight:700;color:#A8DABB;">'+reuEsc(sym)+'</td>'+
        '<td style="padding:7px 8px;font-size:11px;color:#ECEDE3;">'+reuEsc(h.name||h.isin||sym)+'</td>'+
        '<td style="padding:7px 8px;font-size:11px;color:#ECEDE3;text-align:right;">'+(h.quantity!=null?fmt(h.quantity,4):'—')+'</td>'+
        '<td style="padding:7px 8px;font-size:11px;color:#ECEDE3;text-align:right;">'+(h.lastPrice!=null?'$'+fmt(h.lastPrice):'—')+'</td>'+
        '<td style="padding:7px 8px;font-size:12px;font-weight:600;color:#ECEDE3;text-align:right;">'+(h.marketValue!=null?fmtMV(parseFloat(h.marketValue)):'—')+'</td>'+
        '<td style="padding:7px 8px;font-size:11px;font-weight:600;color:'+gColor+';text-align:right;">'+fmtGP(h.unrealizedGain!=null?parseFloat(h.unrealizedGain):null)+'</td>'+
        '<td style="padding:7px 8px;font-size:11px;font-weight:600;color:'+gColor+';text-align:right;">'+fmtPct(h.unrealizedGainPct!=null?parseFloat(h.unrealizedGainPct):null)+'</td>'+
        '<td style="padding:7px 8px;text-align:center;">'+hgB+'</td></tr>';
    });
  } else {
    holdRows='<tr><td colspan="8" style="padding:20px;text-align:center;color:#6B8578;font-size:12px;">Sin posiciones registradas</td></tr>';
  }
  var aumStr=client.aum?'$'+Number(client.aum).toLocaleString('en-US'):'—';
  var perfKPIs=[['AUM Declarado',aumStr,'#ECEDE3'],['Valor de Cartera',fmtMV(totMV),'#C9A84C'],['Capital Invertido',hasCost?'$'+fmt(totCost):'—','#ECEDE3'],['Ganancia No Realizada',fmtGP(totGain),gainColor],['Retorno Total',fmtPct(totGainPct),gainColor],['N° de Posiciones',String(holdings.length),'#ECEDE3']];
  var perfHTML=perfKPIs.map(function(r){
    return '<tr><td style="padding:7px 0;font-size:10px;color:#6B8578;letter-spacing:.5px;">'+r[0]+'</td><td style="padding:7px 0;font-size:14px;font-weight:700;color:'+r[2]+';text-align:right;font-family:\'Playfair Display\',serif;">'+reuEsc(r[1])+'</td></tr>';
  }).join('');
  var notesHTML='';
  if(notes&&notes.length){
    var rn=notes.slice(-5).reverse();
    var nr=rn.map(function(n){var nd=n.date?n.date.split('T')[0]:'';return '<tr><td style="padding:5px 8px;font-size:10px;color:#6B8578;white-space:nowrap;vertical-align:top;">'+reuEsc(nd)+'</td><td style="padding:5px 8px;font-size:11px;color:#ECEDE3;line-height:1.5;">'+reuEsc(n.texto||n.text||n.notas||'')+'</td></tr>';}).join('');
    notesHTML='<div style="background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:10px;padding:20px;margin-bottom:28px;"><div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:14px;">Historial de Actividad</div><table style="width:100%;border-collapse:collapse;">'+nr+'</table></div>';
  }
  var agendaHTML='';
  if(meeting.agenda){agendaHTML='<div style="background:rgba(201,168,76,.06);border:1px solid rgba(201,168,76,.2);border-left:3px solid #C9A84C;border-radius:8px;padding:16px 20px;margin-bottom:28px;"><div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:8px;">Agenda</div><div style="font-size:13px;color:#ECEDE3;line-height:1.7;">'+reuEsc(meeting.agenda)+'</div></div>';}
  return '<div style="background:#0a1f1b;padding:48px;font-family:Inter,sans-serif;color:#ECEDE3;width:794px;box-sizing:border-box;">'+
    '<div style="display:flex;justify-content:space-between;align-items:flex-end;border-bottom:1px solid rgba(201,168,76,.25);padding-bottom:24px;margin-bottom:36px;">'+
      '<div><div style="font-family:\'Playfair Display\',serif;font-size:26px;color:#C9A84C;letter-spacing:3px;font-weight:600;">EXPRESSLINE</div><div style="font-size:9px;letter-spacing:3px;color:#6B8578;margin-top:4px;text-transform:uppercase;">Dashboard Offshore</div><div style="width:40px;height:2px;background:#C9A84C;margin-top:8px;"></div></div>'+
      '<div style="text-align:right;"><div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:#6B8578;">Informe de Reunión</div><div style="font-size:13px;color:#A8DABB;margin-top:5px;font-weight:500;">'+reuEsc(mds)+(meeting.time?' &middot; '+reuEsc(meeting.time):'')+'</div></div>'+
    '</div>'+
    '<div style="margin-bottom:32px;"><div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#6B8578;margin-bottom:8px;">Cliente</div><div style="font-family:\'Playfair Display\',serif;font-size:32px;color:#ECEDE3;font-weight:600;line-height:1.1;">'+reuEsc(cname)+'</div>'+(client.sociedad?'<div style="font-size:12px;color:#6B8578;margin-top:5px;letter-spacing:.5px;">'+reuEsc(client.sociedad)+'</div>':'')+'<div style="width:52px;height:2px;background:#C9A84C;margin-top:10px;"></div></div>'+
    agendaHTML+
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px;">'+
      '<div style="background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:10px;padding:20px;"><div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:14px;">Perfil del Cliente</div><table style="width:100%;border-collapse:collapse;">'+profHTML+'</table></div>'+
      '<div style="background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:10px;padding:20px;"><div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:14px;">Performance</div><table style="width:100%;border-collapse:collapse;">'+perfHTML+'</table></div>'+
    '</div>'+
    '<div style="background:rgba(13,41,36,.7);border:1px solid rgba(168,218,187,.12);border-radius:10px;padding:20px;margin-bottom:28px;">'+
      '<div style="font-size:9px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:#C9A84C;margin-bottom:16px;">Cartera</div>'+
      '<table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:1px solid rgba(168,218,187,.15);">'+
        '<th style="padding:7px 8px;text-align:left;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Ticker</th>'+
        '<th style="padding:7px 8px;text-align:left;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Activo</th>'+
        '<th style="padding:7px 8px;text-align:right;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Cantidad</th>'+
        '<th style="padding:7px 8px;text-align:right;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Precio</th>'+
        '<th style="padding:7px 8px;text-align:right;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Val. Mercado</th>'+
        '<th style="padding:7px 8px;text-align:right;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">G/P</th>'+
        '<th style="padding:7px 8px;text-align:right;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">G/P %</th>'+
        '<th style="padding:7px 8px;text-align:center;color:#6B8578;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">Señal</th>'+
      '</tr></thead><tbody>'+holdRows+'</tbody>'+
      '<tfoot><tr style="border-top:1px solid rgba(201,168,76,.3);background:rgba(201,168,76,.06);">'+
        '<td colspan="4" style="padding:10px 8px;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#C9A84C;font-weight:700;">Total Cartera</td>'+
        '<td style="padding:10px 8px;text-align:right;font-family:\'Playfair Display\',serif;font-size:14px;font-weight:700;color:#C9A84C;">'+fmtMV(totMV)+'</td>'+
        '<td style="padding:10px 8px;text-align:right;font-size:12px;font-weight:700;color:'+gainColor+';">'+fmtGP(totGain)+'</td>'+
        '<td style="padding:10px 8px;text-align:right;font-size:12px;font-weight:700;color:'+gainColor+';">'+fmtPct(totGainPct)+'</td>'+
        '<td></td></tr></tfoot></table></div>'+
    notesHTML+
    '<div style="border-top:1px solid rgba(168,218,187,.1);padding-top:16px;display:flex;justify-content:space-between;align-items:center;">'+
      '<div style="font-size:9px;color:rgba(107,133,120,.5);letter-spacing:1.5px;text-transform:uppercase;">Express Line · Uso interno · Confidencial</div>'+
      '<div style="font-size:9px;color:rgba(107,133,120,.5);">Generado el '+reuEsc(todayStr)+'</div>'+
    '</div></div>';
}
"""

OLD_SCRIPT_END = (
    "  hoverEl.addEventListener('mouseleave',function(){\n"
    "    cxEl.setAttribute('x1','-1'); cxEl.setAttribute('x2','-1');\n"
    "    cyEl.setAttribute('y1','-1'); cyEl.setAttribute('y2','-1');\n"
    "    dotEl.setAttribute('cx','-10'); dotEl.setAttribute('cy','-10');\n"
    "    tipEl.style.display='none';\n"
    "  });\n"
    "}\n"
    "</script>"
)
NEW_SCRIPT_END = OLD_SCRIPT_END.replace('\n</script>', JS + '\n</script>')

if 'reuBuildPDFHTML' in html:
    print('Paso 4 ya aplicado — saltando JS')
elif OLD_SCRIPT_END not in html:
    print('ERROR: no se encontro el ancla del </script> final')
    sys.exit(1)
else:
    html = html.replace(OLD_SCRIPT_END, NEW_SCRIPT_END, 1)
    print('OK Paso 4: JS agregado')

# ══════════════════════════════════════════════════════════════
# Verificaciones finales
# ══════════════════════════════════════════════════════════════
assert 'reu-layout' in html, 'FALLA: CSS no esta'
assert 'initReuniones' in html, 'FALLA: JS no esta'
assert 'page-reuniones' in html, 'FALLA: HTML no esta'
assert 'reu-modal-bg' in html, 'FALLA: modal no esta'
assert 'reuBuildPDFHTML' in html, 'FALLA: PDF builder no esta'

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nListo — {FILE} actualizado.')
print(f'Caracteres: {len(original)} -> {len(html)} (+{len(html)-len(original)})')
