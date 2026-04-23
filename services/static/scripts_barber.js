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
(function buildHorariosFuncionamento(){
  var dias = [
    { key: 'dom', label: 'Domingo' },
    { key: 'seg', label: 'Segunda' },
    { key: 'ter', label: 'Terça'   },
    { key: 'qua', label: 'Quarta'  },
    { key: 'qui', label: 'Quinta'  },
    { key: 'sex', label: 'Sexta'   },
    { key: 'sab', label: 'Sábado'  },
  ];

  // var defaults = {
  //   dom: { aberto: false, abertura: '08:00', fechamento: '18:00' },
  //   seg: { aberto: true,  abertura: '08:00', fechamento: '20:00' },
  //   ter: { aberto: true,  abertura: '08:00', fechamento: '20:00' },
  //   qua: { aberto: true,  abertura: '08:00', fechamento: '20:00' },
  //   qui: { aberto: true,  abertura: '08:00', fechamento: '20:00' },
  //   sex: { aberto: true,  abertura: '08:00', fechamento: '20:00' },
  //   sab: { aberto: true,  abertura: '09:00', fechamento: '18:00' },
  // };
  
  var defaults = operatingHours
  console.log('Horários carregados:', defaults);

  /* Slots disponíveis: 06:00 até 23:00, de 30 em 30 min */
  var TIME_SLOTS = [];
  for (var h = 6; h <= 23; h++) {
    TIME_SLOTS.push(pad(h) + ':00');
    if (h < 23) TIME_SLOTS.push(pad(h) + ':30');
  }

  /* Estado: qual dropdown está aberto no momento */
  var activeDropdown = null;

  function closeActiveDropdown() {
    if (activeDropdown) {
      activeDropdown.style.display = 'none';
      activeDropdown = null;
    }
  }

  /* Fecha ao clicar fora */
  document.addEventListener('click', function(e) {
    if (activeDropdown && !activeDropdown.contains(e.target) && !e.target.closest('.hf-time-btn')) {
      closeActiveDropdown();
    }
  });

  function buildTimeDropdown(key, tipo, currentValue, hiddenInput) {
    var drop = document.createElement('div');
    drop.className = 'hf-time-dropdown';
    drop.style.cssText = 'display:none;position:absolute;top:calc(100% + 4px);left:0;z-index:999;' +
      'background:var(--surface,#1a1a1a);border:1px solid var(--border,#333);border-radius:8px;' +
      'max-height:220px;overflow-y:auto;min-width:90px;box-shadow:0 8px 24px rgba(0,0,0,.4);';

    TIME_SLOTS.forEach(function(slot) {
      var opt = document.createElement('div');
      opt.className = 'hf-time-opt';
      opt.textContent = slot;
      opt.style.cssText = 'padding:8px 16px;cursor:pointer;font-size:13px;font-family:monospace;' +
        'transition:background .15s;' + (slot === currentValue ? 'color:var(--gold,#c9a84c);font-weight:700;' : '');

      opt.addEventListener('mouseenter', function() { this.style.background = 'rgba(255,255,255,.07)'; });
      opt.addEventListener('mouseleave', function() { this.style.background = ''; });

      opt.addEventListener('click', function(e) {
        e.stopPropagation();
        /* Atualiza o hidden input */
        hiddenInput.value = slot;
        /* Atualiza o label do botão */
        var btn = hiddenInput.closest('.hf-time-wrap').querySelector('.hf-time-btn');
        btn.querySelector('.hf-time-label').textContent = slot;
        closeActiveDropdown();
      });

      drop.appendChild(opt);
    });

    return drop;
  }

  function buildTimeWrap(key, tipo, value) {
    var wrap = document.createElement('div');
    wrap.className = 'hf-time-wrap';
    wrap.style.cssText = 'position:relative;display:inline-block;';

    /* Input hidden — é isso que o form vai submeter */
    var hidden = document.createElement('input');
    hidden.type  = 'hidden';
    hidden.name  = 'hf_' + key + '_' + tipo;
    hidden.value = value;
    wrap.appendChild(hidden);

    /* Botão visível */
    var btn = document.createElement('button');
    btn.type      = 'button';
    btn.className = 'hf-time-btn';
    btn.style.cssText = 'display:flex;align-items:center;gap:6px;padding:6px 12px;' +
      'background:var(--surface2,#242424);border:1px solid var(--border,#333);border-radius:6px;' +
      'color:var(--text,#fff);font-size:13px;font-family:monospace;cursor:pointer;transition:border-color .2s;';
    btn.innerHTML = '<span class="hf-time-label">' + value + '</span>' +
                   '<i class="fa-solid fa-chevron-down" style="font-size:10px;opacity:.6;"></i>';

    btn.addEventListener('mouseenter', function() { this.style.borderColor = 'var(--gold,#c9a84c)'; });
    btn.addEventListener('mouseleave', function() { this.style.borderColor = 'var(--border,#333)'; });

    var drop = buildTimeDropdown(key, tipo, value, hidden);
    wrap.appendChild(drop);

    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var isOpen = drop.style.display !== 'none';
      closeActiveDropdown();
      if (!isOpen) {
        drop.style.display = 'block';
        activeDropdown = drop;
        /* Scroll até o item selecionado */
        var selected = drop.querySelector('.hf-time-opt[style*="gold"]');
        if (selected) selected.scrollIntoView({ block: 'center' });
      }
    });

    wrap.insertBefore(btn, hidden);
    return wrap;
  }

  /* ── Monta as linhas ── */
  var wrap = document.getElementById('horarios-funcionamento');
  if (!wrap) return;

  dias.forEach(function(dia) {
    var d = defaults[dia.key];
    var row = document.createElement('div');
    row.className = 'hf-row';

    /* Label do dia */
    var label = document.createElement('div');
    label.className = 'hf-day-label';
    label.textContent = dia.label;
    row.appendChild(label);

    /* Toggle aberto/fechado */
    var toggleLabel = document.createElement('label');
    toggleLabel.className = 'toggle';
    toggleLabel.style.flexShrink = '0';
    toggleLabel.innerHTML =
      '<input type="checkbox" name="hf_' + dia.key + '_aberto" id="hf-' + dia.key + '-aberto"' +
      (d.aberto ? ' checked' : '') + '/>' +
      '<span class="toggle-track"></span>';
    row.appendChild(toggleLabel);

    /* Container dos horários */
    var timesEl = document.createElement('div');
    timesEl.id = 'hf-' + dia.key + '-times';
    timesEl.className = 'hf-times';
    timesEl.style.display = d.aberto ? 'flex' : 'none';
    timesEl.style.alignItems = 'center';
    timesEl.style.gap = '15px';

    timesEl.appendChild(buildTimeWrap(dia.key, 'abertura',    d.abertura));

    var sep = document.createElement('span');
    sep.className = 'hf-sep';
    sep.textContent = 'até';
    timesEl.appendChild(sep);

    timesEl.appendChild(buildTimeWrap(dia.key, 'fechamento', d.fechamento));
    row.appendChild(timesEl);

    /* Badge "Fechado" */
    var closedEl = document.createElement('div');
    closedEl.id = 'hf-' + dia.key + '-closed';
    closedEl.style.cssText = 'display:' + (d.aberto ? 'none' : 'flex') + ';align-items:center;';
    closedEl.innerHTML = '<span class="badge badge-alert">Fechado</span>';
    row.appendChild(closedEl);

    /* Evento do toggle */
    var checkbox = toggleLabel.querySelector('input');
    checkbox.addEventListener('change', function() {
      timesEl.style.display  = this.checked ? 'flex' : 'none';
      closedEl.style.display = this.checked ? 'none' : 'flex';
    });

    wrap.appendChild(row);
  });
})();

/* ──────────────────────────────────────────────
   INIT
────────────────────────────────────────────── */
buildPickMonthList();
buildDefaultHoursCard();