/* ══════════════════════════════════════════════
   DADOS — No Django, injete:
     var DIAS_OFF   = {{ dias_off_json|safe }};   // ex: ["2026-03-10","2026-03-15"]
     var HORARIOS   = {{ horarios_json|safe }};   // ex: {"2026-03-20":["09:00","10:00",...]}
   Por ora usamos defaults vazios.
══════════════════════════════════════════════ */
var DIAS_OFF = [];   // array de datas "YYYY-MM-DD" marcadas como folga
var HORARIOS = {};   // objeto: data -> array de horários bloqueados (desativados)

/* Horários padrão gerados (30 min, 09-20h) */
var DEFAULT_SLOTS = [];
(function(){
  for(var h=9; h<20; h++){
    DEFAULT_SLOTS.push(pad(h)+':00');
    DEFAULT_SLOTS.push(pad(h)+':30');
  }
})();

function pad(n){ return n < 10 ? '0'+n : ''+n; }

/* ──────────────────────────────────────────────
   TABS
────────────────────────────────────────────── */
function switchTab(id, el){
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('panel-'+id).classList.add('active');
  el.classList.add('active');
}

/* ──────────────────────────────────────────────
   MODALS
────────────────────────────────────────────── */
function openModal(id){
  document.getElementById(id).classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id){
  document.getElementById(id).classList.remove('open');
  document.body.style.overflow = '';
}
function closeOnBg(e, id){
  if(e.target === document.getElementById(id)) closeModal(id);
}

/* ──────────────────────────────────────────────
   TOAST
────────────────────────────────────────────── */
function showToast(msg, type){
  var wrap = document.getElementById('toast-wrap');
  var t = document.createElement('div');
  t.className = 'toast ' + (type||'');
  t.innerHTML = (type==='success' ? '<i class="fa-solid fa-check" style="margin-right:8px;"></i>' :
                 type==='error'   ? '<i class="fa-solid fa-xmark" style="margin-right:8px;"></i>' :
                 '<i class="fa-solid fa-circle-info" style="margin-right:8px;"></i>') + msg;
  wrap.appendChild(t);
  requestAnimationFrame(function(){ t.classList.add('show'); });
  setTimeout(function(){ t.classList.remove('show'); setTimeout(function(){ t.remove(); }, 350); }, 2800);
}

/* ──────────────────────────────────────────────
   MONTHS LIST
────────────────────────────────────────────── */
var MONTHS_PT = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];

function buildMonthList(){
  var el = document.getElementById('month-list');
  el.innerHTML = '';
  var now = new Date();
  var curM = now.getMonth(); // 0-11
  var curY = now.getFullYear();

  // Mostrar mês atual + próximos 11
  for(var i=0; i<12; i++){
    var m = (curM + i) % 12;
    var y = curY + Math.floor((curM + i) / 12);
    var label = MONTHS_PT[m] + ' ' + y;

    // Contar dias off neste mês
    var prefix = y+'-'+pad(m+1)+'-';
    var offs = DIAS_OFF.filter(function(d){ return d.startsWith(prefix); }).length;

    var badge = offs === 0
      ? '<span class="month-badge badge-gray">Sem folgas</span>'
      : '<span class="month-badge badge-alert">'+offs+' folga'+(offs>1?'s':'')+'</span>';

    var item = document.createElement('div');
    item.className = 'month-item';
    item.dataset.month = m;
    item.dataset.year  = y;
    item.innerHTML =
      '<div class="month-left">'+
        '<div class="month-icon"><i class="fa-regular fa-calendar-days"></i></div>'+
        '<div>'+
          '<div class="month-name">'+label+'</div>'+
          '<div class="month-stat">'+(i===0?'Mês atual':'')+(offs>0?' · '+offs+' dia(s) configurado(s)':'')+'</div>'+
        '</div>'+
      '</div>'+
      '<div style="display:flex;align-items:center;gap:10px;">'+
        badge+
        '<i class="fa-solid fa-chevron-right month-chevron"></i>'+
      '</div>';

    item.addEventListener('click', function(){
      openMonthModal(parseInt(this.dataset.month), parseInt(this.dataset.year));
    });
    el.appendChild(item);
  }
}

/* ──────────────────────────────────────────────
   MODAL MESES — estado
────────────────────────────────────────────── */
var mState = {
  month: 0, year: 0,
  selectedDay: null,
  // dayData: { "YYYY-MM-DD": { off: bool, slots: ["09:00",...] } }
  dayData: {}
};

function openMonthModal(m, y){
  mState.month = m;
  mState.year  = y;
  mState.selectedDay = null;
  mState.dayData = {};

  // Carrega DIAS_OFF e HORARIOS para este mês
  var prefix = y+'-'+pad(m+1)+'-';
  DIAS_OFF.forEach(function(d){
    if(d.startsWith(prefix)){
      if(!mState.dayData[d]) mState.dayData[d] = { off: false, slots: [] };
      mState.dayData[d].off = true;
      mState.dayData[d].slots = [];
    }
  });
  Object.keys(HORARIOS).forEach(function(d){
    if(d.startsWith(prefix)){
      if(!mState.dayData[d]) mState.dayData[d] = { off: false, slots: DEFAULT_SLOTS.slice() };
      mState.dayData[d].slots = HORARIOS[d]; // horários ATIVOS (não bloqueados)
    }
  });

  document.getElementById('modal-month-title').textContent = MONTHS_PT[m]+' '+y;
  document.getElementById('m-cal-title').textContent = MONTHS_PT[m].toUpperCase()+' '+y;

  renderMonthCal();
  document.getElementById('day-config').style.display = 'none';
  openModal('modal-month');
}

function renderMonthCal(){
  var el = document.getElementById('m-cal-days');
  el.innerHTML = '';
  var m = mState.month, y = mState.year;
  var firstDay = new Date(y, m, 1).getDay(); // 0=dom
  var daysInMonth = new Date(y, m+1, 0).getDate();
  var today = new Date(); today.setHours(0,0,0,0);

  // Blanks
  for(var b=0; b<firstDay; b++){
    var blank = document.createElement('div');
    blank.className = 'm-day empty';
    el.appendChild(blank);
  }

  for(var d=1; d<=daysInMonth; d++){
    var dateObj = new Date(y, m, d);
    dateObj.setHours(0,0,0,0);
    var dateStr = y+'-'+pad(m+1)+'-'+pad(d);
    var dd = document.createElement('div');
    dd.className = 'm-day';
    dd.dataset.date = dateStr;
    dd.dataset.day  = d;

    if(dateObj < today) dd.classList.add('past');
    else if(dateObj.getTime() === today.getTime()) dd.classList.add('today');

    var data = mState.dayData[dateStr];
    if(data && data.off) dd.classList.add('off');

    if(mState.selectedDay === dateStr) dd.classList.add('today'); // highlight selected

    dd.innerHTML = '<span class="m-day-num">'+d+'</span>';

    if(!dd.classList.contains('past')){
      dd.addEventListener('click', function(){
        selectDay(this.dataset.date, parseInt(this.dataset.day));
      });
    }
    el.appendChild(dd);
  }
}

function selectDay(dateStr, dayNum){
  mState.selectedDay = dateStr;

  // Highlight
  document.querySelectorAll('#m-cal-days .m-day').forEach(function(d){
    d.style.outline = '';
  });
  var sel = document.querySelector('#m-cal-days .m-day[data-date="'+dateStr+'"]');
  if(sel) sel.style.outline = '2px solid var(--gold)';

  var dow = new Date(mState.year, mState.month, dayNum).getDay();
  var DAYS = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
  document.getElementById('day-config-label').textContent =
    DAYS[dow]+', '+pad(dayNum)+' de '+MONTHS_PT[mState.month]+' '+mState.year;

  document.getElementById('day-config').style.display = 'block';
  renderTimeGrid(dateStr);
}

function getDayData(dateStr){
  if(!mState.dayData[dateStr]){
    mState.dayData[dateStr] = { off: false, slots: DEFAULT_SLOTS.slice() };
  }
  return mState.dayData[dateStr];
}

function renderTimeGrid(dateStr){
  var grid = document.getElementById('m-time-grid');
  grid.innerHTML = '';
  var data = getDayData(dateStr);

  if(data.off){
    grid.innerHTML = '<p style="color:var(--red);font-size:13px;grid-column:1/-1;padding:10px 0;"><i class="fa-solid fa-ban"></i> Dia marcado como folga — sem atendimentos.</p>';
    return;
  }

  DEFAULT_SLOTS.forEach(function(slot){
    var btn = document.createElement('div');
    btn.className = 't-slot ' + (data.slots.indexOf(slot) !== -1 ? 'active' : 'off');
    btn.textContent = slot;
    btn.title = 'Clique para alternar';
    btn.addEventListener('click', function(){
      toggleSlot(dateStr, slot, btn);
    });
    grid.appendChild(btn);
  });
}

function toggleSlot(dateStr, slot, el){
  var data = getDayData(dateStr);
  var idx = data.slots.indexOf(slot);
  if(idx === -1){ data.slots.push(slot); el.classList.remove('off'); el.classList.add('active'); }
  else          { data.slots.splice(idx,1); el.classList.remove('active'); el.classList.add('off'); }
}

/* Botões rápidos */
function markDayOff(){
  if(!mState.selectedDay) return;
  getDayData(mState.selectedDay).off   = true;
  getDayData(mState.selectedDay).slots = [];
  updateDayCalClass(mState.selectedDay, true);
  renderTimeGrid(mState.selectedDay);
  showToast('Dia marcado como folga', 'success');
}
function markDayOn(){
  if(!mState.selectedDay) return;
  getDayData(mState.selectedDay).off   = false;
  getDayData(mState.selectedDay).slots = DEFAULT_SLOTS.slice();
  updateDayCalClass(mState.selectedDay, false);
  renderTimeGrid(mState.selectedDay);
  showToast('Dia liberado com todos os horários', 'success');
}
function setMorningOnly(){
  if(!mState.selectedDay) return;
  var d = getDayData(mState.selectedDay);
  d.off = false;
  d.slots = DEFAULT_SLOTS.filter(function(s){ return parseInt(s.split(':')[0]) < 12; });
  renderTimeGrid(mState.selectedDay);
  showToast('Somente manhã ativada (09h–12h)', 'success');
}
function setAfternoonOnly(){
  if(!mState.selectedDay) return;
  var d = getDayData(mState.selectedDay);
  d.off = false;
  d.slots = DEFAULT_SLOTS.filter(function(s){ return parseInt(s.split(':')[0]) >= 12; });
  renderTimeGrid(mState.selectedDay);
  showToast('Somente tarde ativada (12h–20h)', 'success');
}
function setAllSlots(){
  if(!mState.selectedDay) return;
  var d = getDayData(mState.selectedDay);
  d.off = false; d.slots = DEFAULT_SLOTS.slice();
  renderTimeGrid(mState.selectedDay);
  showToast('Todos os horários ativados', 'success');
}
function clearAllSlots(){
  if(!mState.selectedDay) return;
  var d = getDayData(mState.selectedDay);
  d.off = false; d.slots = [];
  renderTimeGrid(mState.selectedDay);
  showToast('Todos os horários desativados', '');
}

function updateDayCalClass(dateStr, isOff){
  var el = document.querySelector('#m-cal-days .m-day[data-date="'+dateStr+'"]');
  if(!el) return;
  if(isOff) el.classList.add('off'); else el.classList.remove('off');
}

function saveMonthConfig(){
  /* Não faz nada aqui — o submit do form-month chama prepareMonthForm() antes */
}

function prepareMonthForm(){
  /* Monta os hidden inputs com o estado atual antes do form submeter */
  var diasOff = [];
  var horariosConfig = {};
  Object.keys(mState.dayData).forEach(function(dateStr){
    var d = mState.dayData[dateStr];
    if(d.off) diasOff.push(dateStr);
    else if(d.slots.length) horariosConfig[dateStr] = d.slots;
  });
  document.getElementById('fm-ano').value      = mState.year;
  document.getElementById('fm-mes').value      = mState.month + 1;
  document.getElementById('fm-dias-off').value = JSON.stringify(diasOff);
  document.getElementById('fm-horarios').value = JSON.stringify(horariosConfig);
  /* O form submete normalmente após este return */
}

/* ──────────────────────────────────────────────
   HORÁRIOS PADRÃO
────────────────────────────────────────────── */
var DAYS_LABEL = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
var defaultWorkDays = { 0:false, 1:true, 2:true, 3:true, 4:true, 5:true, 6:true };
var defaultHours = { start:'09:00', end:'20:00', lunchStart:'12:00', lunchEnd:'13:00', lunchBreak: false };

function buildDefaultHoursCard(){
  var card = document.getElementById('default-hours-card');
  card.innerHTML = '<div class="card-title">Dias e Horários</div><div class="card-sub">Configure para cada dia da semana</div>';

  DAYS_LABEL.forEach(function(name, dow){
    var row = document.createElement('div');
    row.className = 'toggle-row';
    row.innerHTML =
      '<div style="flex:1;">'+
        '<div class="toggle-label">'+name+'</div>'+
        (defaultWorkDays[dow] ?
          '<div class="toggle-sub" id="dh-sub-'+dow+'">09:00 às 20:00</div>' :
          '<div class="toggle-sub" id="dh-sub-'+dow+'">Não trabalha</div>')+
      '</div>'+
      '<div style="display:flex;align-items:center;gap:10px;">'+
        (defaultWorkDays[dow] ?
          '<button class="q-btn" style="font-size:11px;padding:5px 10px;" onclick="editDayHours('+dow+')"><i class="fa-regular fa-clock"></i> Editar</button>' : '')+
        '<label class="toggle">'+
          '<input type="checkbox" id="dh-toggle-'+dow+'" '+(defaultWorkDays[dow]?'checked':'')+' onchange="toggleWorkDay('+dow+', this)"/>'+
          '<span class="toggle-track"></span>'+
        '</label>'+
      '</div>';
    card.appendChild(row);
  });
}

function toggleWorkDay(dow, el){
  defaultWorkDays[dow] = el.checked;
  buildDefaultHoursCard();
}
function editDayHours(dow){
  /* Abre um modal menor ou redireciona — implemente conforme seu fluxo */
  showToast('Edição de horário para '+DAYS_LABEL[dow], '');
}

/* ──────────────────────────────────────────────
   SERVIÇOS — preenche modais via data-attributes
   Nenhuma requisição JS aqui: o submit do form cuida de tudo.
────────────────────────────────────────────── */
function openEditService(btn){
  var d = btn.dataset;
  document.getElementById('es-id').value      = d.id;
  document.getElementById('es-nome').value    = d.nome;
  document.getElementById('es-desc').value    = d.desc;
  document.getElementById('es-preco').value   = d.preco;
  document.getElementById('es-duracao').value = d.duracao;
  document.getElementById('es-icone').value   = d.icone;
  document.getElementById('es-ativo').checked = d.ativo === '1';
  /* Action dinâmico: /barbeiro/servicos/<id>/editar/ */
  document.getElementById('form-edit-service').action =
    '/barbeiro/servicos/' + d.id + '/editar/';
  openModal('modal-edit-service');
}

function openDeleteService(btn){
  var d = btn.dataset;
  document.getElementById('del-id').value   = d.id;
  document.getElementById('del-nome').textContent = '"' + d.nome + '"';
  /* Action dinâmico: /barbeiro/servicos/<id>/excluir/ */
  document.getElementById('form-delete-service').action =
    '/barbeiro/servicos/' + d.id + '/excluir/';
  openModal('modal-delete-confirm');
}

/* ──────────────────────────────────────────────
   INIT
────────────────────────────────────────────── */
buildMonthList();
buildDefaultHoursCard();
