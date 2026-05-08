/* ══════════════════════════════════════════════
   DADOS — No Django, injete:
     var DIAS_OFF   = {{ dias_off_json|safe }};
     var HORARIOS   = {{ horarios_json|safe }};
   Por ora usamos defaults vazios.
══════════════════════════════════════════════ */
var DIAS_OFF = [];
var HORARIOS = {};

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

/* ──────────────────────────────────────────────
   MODAL MESES — estado
────────────────────────────────────────────── */
var mState = {
  month: 0, year: 0,
  selectedDay: null,
  dayData: {}
};

function openMonthModal(m, y){
  mState.month = m;
  mState.year  = y;
  mState.selectedDay = null;
  mState.dayData = {};

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
      mState.dayData[d].slots = HORARIOS[d];
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
  var firstDay = new Date(y, m, 1).getDay();
  var daysInMonth = new Date(y, m+1, 0).getDate();
  var today = new Date(); today.setHours(0,0,0,0);

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

    if(mState.selectedDay === dateStr) dd.classList.add('today');

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

/* ──────────────────────────────────────────────
   HORÁRIOS PADRÃO
────────────────────────────────────────────── */
var DAYS_LABEL = ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'];
var defaultWorkDays = { 0:false, 1:true, 2:true, 3:true, 4:true, 5:true, 6:true };

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
  showToast('Edição de horário para '+DAYS_LABEL[dow], '');
}

/* ──────────────────────────────────────────────
   SERVIÇOS — preenche modais via data-attributes
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
  openModal('modal-edit-service');
}

function openDeleteService(btn){
  var d = btn.dataset;
  document.getElementById('del-id').value = d.id;
  document.getElementById('del-nome').textContent = '"' + d.nome + '"';
  openModal('modal-delete-confirm');
}

/* ──────────────────────────────────────────────
   PICK MONTH
────────────────────────────────────────────── */
var openedMonths = [];

function buildPickMonthList(){
  var el = document.getElementById('month-pick-list');
  el.innerHTML = '';
  var now = new Date();
  var curM = now.getMonth();
  var curY = now.getFullYear();

  for(var i=0; i<12; i++){
    var m = (curM + i) % 12;
    var y = curY + Math.floor((curM + i) / 12);
    var label = MONTHS_PT[m] + ' ' + y;
    var alreadyOpen = openedMonths.some(function(o){ return o.m === m && o.y === y; });

    var item = document.createElement('div');
    item.className = 'month-pick-item';
    item.dataset.m = m;
    item.dataset.y = y;
    item.innerHTML =
      '<span>' + label + '</span>' +
      (alreadyOpen
        ? '<span style="font-size:11px;color:var(--gold);font-family:\'Barlow Condensed\',sans-serif;letter-spacing:1px;"><i class="fa-solid fa-check" style="margin-right:4px;"></i>Aberta</span>'
        : '<i class="fa-solid fa-chevron-right" style="color:var(--gray);font-size:12px;"></i>');

    item.addEventListener('click', function(){
      var m2 = parseInt(this.dataset.m);
      var y2 = parseInt(this.dataset.y);
      if(!openedMonths.some(function(o){ return o.m === m2 && o.y === y2; })){
        openedMonths.push({ m: m2, y: y2 });
        renderOpenMonthsList();
      }
      closeModal('modal-pick-month');
      openMonthModal(m2, y2);
    });
    el.appendChild(item);
  }
}

function renderOpenMonthsList(){
  var el = document.getElementById('open-months-list');
  el.innerHTML = '';
  if(!openedMonths.length) return;

  openedMonths.forEach(function(o){
    var label = MONTHS_PT[o.m] + ' ' + o.y;
    var prefix = o.y + '-' + pad(o.m + 1) + '-';
    var offs = DIAS_OFF.filter(function(d){ return d.startsWith(prefix); }).length;

    var bar = document.createElement('div');
    bar.className = 'open-month-bar';
    bar.innerHTML =
      '<div class="open-month-bar-left">' +
        '<div class="open-month-bar-icon"><i class="fa-regular fa-calendar-days"></i></div>' +
        '<div>' +
          '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:17px;letter-spacing:2px;">' + label + '</div>' +
          '<div style="font-size:11px;color:var(--gray);margin-top:2px;">' +
            (offs > 0 ? offs + ' dia(s) com folga' : 'Sem folgas configuradas') +
          '</div>' +
        '</div>' +
      '</div>' +
      '<i class="fa-solid fa-chevron-right" style="color:var(--gray);font-size:13px;"></i>';

    bar.addEventListener('click', function(){
      openMonthModal(o.m, o.y);
    });
    el.appendChild(bar);
  });
}






/* ══════════════════════════════════════
   HORÁRIOS DE FUNCIONAMENTO — Estabelecimento
══════════════════════════════════════ */


/* ──────────────────────────────────────────────
   INIT
────────────────────────────────────────────── */
buildPickMonthList();
buildDefaultHoursCard();