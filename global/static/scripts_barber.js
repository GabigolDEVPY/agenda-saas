/* Admin — agenda, serviços e funcionários */
var DIAS_OFF = [];
var HORARIOS = {};

/* horarios que aparecerão na agenda para selecionar horarios disponiveis para agendar
 pode alterar e mandar do backend, da parte de avaliable days, hours, etc*/
var DEFAULT_SLOTS = [];
(function() {
  var h;
  for (h = 6; h < 23; h++) {
    DEFAULT_SLOTS.push(pad(h) + ':00');
    DEFAULT_SLOTS.push(pad(h) + ':30');
  }
})();

var DOW_MAP = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sab'];

function getOperatingHoursSlots(dateObj) {
  var dow = dateObj.getDay();
  var key = DOW_MAP[dow];
  var oh = typeof operatingHours !== 'undefined' ? operatingHours[key] : null;
  
  if (!oh) {
    return { aberto: true, slots: DEFAULT_SLOTS.slice() };
  }
  if (!oh.aberto) {
    return { aberto: false, slots: [] };
  }
  
  var slots = [];
  var start = oh.abertura.split(':');
  var end = oh.fechamento.split(':');
  var startH = parseInt(start[0], 10);
  var startM = parseInt(start[1], 10);
  var endH = parseInt(end[0], 10);
  var endM = parseInt(end[1], 10);
  
  var h = startH;
  var m = startM;
  while (h < endH || (h === endH && m < endM)) {
    slots.push(pad(h) + ':' + pad(m));
    m += 30;
    if (m >= 60) {
      m -= 60;
      h++;
    }
  }
  return { aberto: true, slots: slots };
}

var MONTHS_PT = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
var DAYS_LABEL = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
var defaultWorkDays = { 0: false, 1: true, 2: true, 3: true, 4: true, 5: true, 6: true };

var openedMonths = [];

var mState = {
  month: 0,
  year: 0,
  selectedDay: null,
  dayData: {}
};

function switchTab(id, el) {
  document.querySelectorAll('.panel').forEach(function(panel) {
    panel.classList.remove('active');
  });
  document.querySelectorAll('.nav-tab').forEach(function(tab) {
    tab.classList.remove('active');
  });
  document.getElementById('panel-' + id).classList.add('active');
  el.classList.add('active');
}

function monthPrefix(y, m) {
  return y + '-' + pad(m + 1) + '-';
}

function openMonthModal(m, y) {
  var prefix = monthPrefix(y, m);
  mState.month = m;
  mState.year = y;
  mState.selectedDay = null;
  mState.dayData = {};

  DIAS_OFF.forEach(function(d) {
    if (!d.startsWith(prefix)) return;
    mState.dayData[d] = { off: true, slots: [] };
  });

  Object.keys(HORARIOS).forEach(function(d) {
    if (!d.startsWith(prefix)) return;
    var bloqueados = HORARIOS[d];
    
    var parts = d.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    
    var ativos = ohSlots.slots.filter(function(s) {
      return bloqueados.indexOf(s) === -1;
    });
    mState.dayData[d] = { off: !ohSlots.aberto, slots: ativos };
  });

  document.getElementById('modal-month-title').textContent = MONTHS_PT[m] + ' ' + y;
  document.getElementById('m-cal-title').textContent = MONTHS_PT[m].toUpperCase() + ' ' + y;
  document.getElementById('day-config').style.display = 'none';
  renderMonthCal();
  openModal('modal-month');
}

function renderMonthCal() {
  var el = document.getElementById('m-cal-days');
  if (!el) return;

  el.innerHTML = '';
  var m = mState.month;
  var y = mState.year;
  var firstDay = new Date(y, m, 1).getDay();
  var daysInMonth = new Date(y, m + 1, 0).getDate();
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var frag = document.createDocumentFragment();
  var b;
  var d;
  var blank;
  var dateObj;
  var dateStr;
  var dd;
  var data;

  for (b = 0; b < firstDay; b++) {
    blank = document.createElement('div');
    blank.className = 'm-day empty';
    frag.appendChild(blank);
  }

  for (d = 1; d <= daysInMonth; d++) {
    dateObj = new Date(y, m, d);
    dateObj.setHours(0, 0, 0, 0);
    dateStr = y + '-' + pad(m + 1) + '-' + pad(d);

    dd = document.createElement('div');
    dd.className = 'm-day';
    dd.dataset.date = dateStr;
    dd.dataset.day = d;

    if (dateObj < today) dd.classList.add('past');
    else if (dateObj.getTime() === today.getTime()) dd.classList.add('today');

    data = getDayData(dateStr);
    if (data && data.off) dd.classList.add('off');
    if (mState.selectedDay === dateStr) dd.classList.add('today');
    dd.innerHTML = '<span class="m-day-num">' + d + '</span>';

    if (!dd.classList.contains('past')) {
      dd.addEventListener('click', function() {
        selectDay(this.dataset.date, parseInt(this.dataset.day, 10));
      });
    }
    frag.appendChild(dd);
  }

  el.appendChild(frag);
}

function selectDay(dateStr, dayNum) {
  mState.selectedDay = dateStr;

  document.querySelectorAll('#m-cal-days .m-day').forEach(function(day) {
    day.style.outline = '';
  });

  var sel = document.querySelector('#m-cal-days .m-day[data-date="' + dateStr + '"]');
  if (sel) sel.style.outline = '2px solid var(--gold)';

  document.getElementById('day-config-label').textContent =
    DAYS_LABEL[new Date(mState.year, mState.month, dayNum).getDay()] + ', ' +
    pad(dayNum) + ' de ' + MONTHS_PT[mState.month] + ' ' + mState.year;
  document.getElementById('day-config').style.display = 'block';
  renderTimeGrid(dateStr);
}

function getDayData(dateStr) {
  if (!mState.dayData[dateStr]) {
    var parts = dateStr.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    mState.dayData[dateStr] = { off: !ohSlots.aberto, slots: ohSlots.slots.slice() };
  }
  return mState.dayData[dateStr];
}

function renderTimeGrid(dateStr) {
  var grid = document.getElementById('m-time-grid');
  if (!grid) return;

  grid.innerHTML = '';
  var parts = dateStr.split('-');
  var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
  var ohSlots = getOperatingHoursSlots(dateObj);

  if (!ohSlots.aberto) {
    grid.innerHTML = '<p class="m-day-off-msg"><i class="fa-solid fa-ban"></i> Dia fechado conforme Horário de Funcionamento.</p>';
    document.querySelector('.quick-btns').style.display = 'none';
    return;
  } else {
    document.querySelector('.quick-btns').style.display = 'flex';
  }

  var data = getDayData(dateStr);

  if (data.off) {
    grid.innerHTML = '<p class="m-day-off-msg"><i class="fa-solid fa-ban"></i> Dia marcado como folga — sem atendimentos.</p>';
    return;
  }

  var frag = document.createDocumentFragment();
  ohSlots.slots.forEach(function(slot) {
    var btn = document.createElement('div');
    btn.className = 't-slot ' + (data.slots.indexOf(slot) !== -1 ? 'active' : 'off');
    btn.textContent = slot;
    btn.title = 'Clique para alternar';
    btn.addEventListener('click', function() {
      toggleSlot(dateStr, slot, btn);
    });
    frag.appendChild(btn);
  });
  grid.appendChild(frag);
}

function toggleSlot(dateStr, slot, el) {
  var data = getDayData(dateStr);
  var idx = data.slots.indexOf(slot);
  if (idx === -1) {
    data.slots.push(slot);
    el.classList.remove('off');
    el.classList.add('active');
  } else {
    data.slots.splice(idx, 1);
    el.classList.remove('active');
    el.classList.add('off');
  }
}

function updateDayCalClass(dateStr, isOff) {
  var el = document.querySelector('#m-cal-days .m-day[data-date="' + dateStr + '"]');
  if (!el) return;
  el.classList.toggle('off', isOff);
}

function applyDaySlots(mutator) {
  if (!mState.selectedDay) return;
  mutator(getDayData(mState.selectedDay));
  renderTimeGrid(mState.selectedDay);
}

function markDayOff() {
  applyDaySlots(function(data) {
    data.off = true;
    data.slots = [];
    updateDayCalClass(mState.selectedDay, true);
  });
}

function markDayOn() {
  applyDaySlots(function(data) {
    var parts = mState.selectedDay.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    data.off = false;
    data.slots = ohSlots.slots.slice();
    updateDayCalClass(mState.selectedDay, false);
  });
}

function setMorningOnly() {
  applyDaySlots(function(data) {
    var parts = mState.selectedDay.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    data.off = false;
    data.slots = ohSlots.slots.filter(function(s) {
      return parseInt(s.split(':')[0], 10) < 12;
    });
  });
}

function setAfternoonOnly() {
  applyDaySlots(function(data) {
    var parts = mState.selectedDay.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    data.off = false;
    data.slots = ohSlots.slots.filter(function(s) {
      return parseInt(s.split(':')[0], 10) >= 12;
    });
  });
}

function setAllSlots() {
  applyDaySlots(function(data) {
    var parts = mState.selectedDay.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);
    data.off = false;
    data.slots = ohSlots.slots.slice();
  });
}

function clearAllSlots() {
  applyDaySlots(function(data) {
    data.off = false;
    data.slots = [];
  });
}

function buildDefaultHoursCard() {
  var card = document.getElementById('default-hours-card');
  if (!card) return;

  card.innerHTML = '<div class="card-title">Dias e Horários</div><div class="card-sub">Configure para cada dia da semana</div>';

  DAYS_LABEL.forEach(function(name, dow) {
    var row = document.createElement('div');
    row.className = 'toggle-row';
    row.innerHTML =
      '<div style="flex:1;">' +
        '<div class="toggle-label">' + name + '</div>' +
        '<div class="toggle-sub" id="dh-sub-' + dow + '">' +
          (defaultWorkDays[dow] ? '09:00 às 20:00' : 'Não trabalha') +
        '</div>' +
      '</div>' +
      '<div style="display:flex;align-items:center;gap:10px;">' +
        (defaultWorkDays[dow]
          ? '<button class="q-btn" style="font-size:11px;padding:5px 10px;" onclick="editDayHours(' + dow + ')"><i class="fa-regular fa-clock"></i> Editar</button>'
          : '') +
        '<label class="toggle">' +
          '<input type="checkbox" id="dh-toggle-' + dow + '" ' + (defaultWorkDays[dow] ? 'checked' : '') +
          ' onchange="toggleWorkDay(' + dow + ', this)"/>' +
          '<span class="toggle-track"></span>' +
        '</label>' +
      '</div>';
    card.appendChild(row);
  });
}

function toggleWorkDay(dow, el) {
  defaultWorkDays[dow] = el.checked;
  buildDefaultHoursCard();
}

function editDayHours() {}

function openEditService(btn) {
  var d = btn.dataset;
  document.getElementById('es-id').value = d.id;
  document.getElementById('es-nome').value = d.nome;
  document.getElementById('es-desc').value = d.desc;
  document.getElementById('es-preco').value = d.preco;
  document.getElementById('es-duracao').value = d.duracao;
  document.getElementById('es-icone').value = d.icone;
  document.getElementById('es-ativo').checked = d.ativo === '1';
  openModal('modal-edit-service');
}

function openDeleteService(btn) {
  document.getElementById('del-id').value = btn.dataset.id;
  document.getElementById('del-nome').textContent = '"' + btn.dataset.nome + '"';
  openModal('modal-delete-confirm');
}

function openChangeEmployeePassword(btn) {
  document.getElementById('pwd-emp-id').value = btn.dataset.id;
  document.getElementById('pwd-emp-nome').textContent = btn.dataset.nome;
  openModal('modal-change-employee-password');
}

function openDeleteEmployee(btn) {
  document.getElementById('del-emp-id').value = btn.dataset.id;
  document.getElementById('del-emp-nome').textContent = '"' + btn.dataset.nome + '"';
  openModal('modal-delete-employee');
}

function buildPickMonthList() {
  var el = document.getElementById('month-pick-list');
  if (!el) return;

  el.innerHTML = '';
  var now = new Date();
  var curM = now.getMonth();
  var curY = now.getFullYear();
  var frag = document.createDocumentFragment();
  var i;
  var m;
  var y;
  var label;
  var alreadyOpen;
  var item;

  for (i = 0; i < 12; i++) {
    m = (curM + i) % 12;
    y = curY + Math.floor((curM + i) / 12);
    label = MONTHS_PT[m] + ' ' + y;
    alreadyOpen = openedMonths.some(function(o) { 
      return parseInt(o.m, 10) === parseInt(m, 10) && parseInt(o.y, 10) === parseInt(y, 10); 
    });

    if (alreadyOpen) {
      continue;
    }

    item = document.createElement('div');
    item.className = 'month-pick-item';
    item.dataset.m = m;
    item.dataset.y = y;
    item.innerHTML =
      '<span>' + label + '</span>' +
      '<i class="fa-solid fa-chevron-right month-pick-arrow"></i>';

    item.addEventListener('click', function() {
      var m2 = parseInt(this.dataset.m, 10);
      var y2 = parseInt(this.dataset.y, 10);
      if (!openedMonths.some(function(o) { return o.m === m2 && o.y === y2; })) {
        openedMonths.push({ m: m2, y: y2 });
        renderOpenMonthsList();
      }
      closeModal('modal-pick-month');
      openMonthModal(m2, y2);
    });
    frag.appendChild(item);
  }

  el.appendChild(frag);
}

function renderOpenMonthsList() {
  var el = document.getElementById('open-months-list');
  if (!el) return;

  el.innerHTML = '';
  if (!openedMonths.length) return;

  var frag = document.createDocumentFragment();
  openedMonths.forEach(function(o) {
    var label = MONTHS_PT[o.m] + ' ' + o.y;
    var offs = DIAS_OFF.filter(function(d) {
      return d.startsWith(monthPrefix(o.y, o.m));
    }).length;

    var bar = document.createElement('div');
    bar.className = 'open-month-bar';
    bar.innerHTML =
      '<div class="open-month-bar-left">' +
        '<div class="open-month-bar-icon"><i class="fa-regular fa-calendar-days"></i></div>' +
        '<div>' +
          '<div class="open-month-title">' + label + '</div>' +
          '<div class="open-month-meta">' +
            (offs > 0 ? offs + ' dia(s) com folga' : 'Sem folgas configuradas') +
          '</div>' +
        '</div>' +
      '</div>' +
      '<i class="fa-solid fa-chevron-right month-pick-arrow"></i>';
    bar.addEventListener('click', function() {
      openMonthModal(o.m, o.y);
    });
    frag.appendChild(bar);
  });
  el.appendChild(frag);
}

renderOpenMonthsList();
buildDefaultHoursCard();

function prepareMonthForm() {
  var diasOff = [];
  var horariosCustom = {};

  Object.keys(mState.dayData).forEach(function(dateStr) {
    var data = mState.dayData[dateStr];
    if (data.off) {
      diasOff.push(dateStr);
      return;
    }

    var parts = dateStr.split('-');
    var dateObj = new Date(parts[0], parseInt(parts[1], 10) - 1, parts[2]);
    var ohSlots = getOperatingHoursSlots(dateObj);

    var bloqueados = ohSlots.slots.filter(function(s) {
      return data.slots.indexOf(s) === -1;
    });

    if (!bloqueados.length) return;

    if (bloqueados.length === ohSlots.slots.length) {
      diasOff.push(dateStr);
      return;
    }

    horariosCustom[dateStr] = bloqueados;
  });

  document.getElementById('fm-ano').value = mState.year;
  document.getElementById('fm-mes').value = mState.month;
  document.getElementById('fm-dias-off').value = JSON.stringify(diasOff);
  document.getElementById('fm-horarios').value = JSON.stringify(horariosCustom);
}

document.body.addEventListener('htmx:configRequest', function(evt) {
  if (evt.detail.elt.id === 'form-month') {
    prepareMonthForm();
    evt.detail.parameters['ano'] = document.getElementById('fm-ano').value;
    evt.detail.parameters['mes'] = document.getElementById('fm-mes').value;
    evt.detail.parameters['dias_off'] = document.getElementById('fm-dias-off').value;
    evt.detail.parameters['horarios'] = document.getElementById('fm-horarios').value;
  }
});

document.body.addEventListener('htmx:afterRequest', function(evt) {
  if (evt.detail.successful && evt.detail.elt.id === 'form-month') {
    closeModal('modal-month');

    var resAno = document.getElementById('fm-ano').value;
    var resMes = document.getElementById('fm-mes').value;
    var y = parseInt(resAno, 10);
    var m = parseInt(resMes, 10); // já é 0-indexed (vem do mState.month via prepareMonthForm)

    // Atualiza DIAS_OFF e HORARIOS para o mês salvo
    var prefix = monthPrefix(y, m);
    DIAS_OFF = DIAS_OFF.filter(function(d) { return !d.startsWith(prefix); });
    Object.keys(HORARIOS).forEach(function(k) {
      if (k.startsWith(prefix)) delete HORARIOS[k];
    });

    var newDiasOff = JSON.parse(document.getElementById('fm-dias-off').value || '[]');
    var newHorarios = JSON.parse(document.getElementById('fm-horarios').value || '{}');

    DIAS_OFF = DIAS_OFF.concat(newDiasOff);
    Object.assign(HORARIOS, newHorarios);

    // openedMonths NÃO é alterado aqui — já foi populado corretamente no clique
    renderOpenMonthsList();
  }
});

/* ═══════════════════════════════════════════
   CONFIG
═══════════════════════════════════════════ */
const TL_HH   = 56;   // px por hora
const TL_FROM = 0;     // hora inicial
const TL_TO   = 24;    // hora final

/* ═══════════════════════════════════════════
   MONTH TOGGLE
═══════════════════════════════════════════ */
function toggleMonth(bar) {
  const list    = bar.nextElementSibling;
  const chevron = bar.querySelector('.month-chevron');
  list.classList.toggle('is-hidden');
  chevron.classList.toggle('fa-chevron-down');
  chevron.classList.toggle('fa-chevron-up');
}

/* ═══════════════════════════════════════════
   DAY TOGGLE (accordion dentro do mês)
═══════════════════════════════════════════ */
function toggleDay(bar) {
  const tl     = bar.nextElementSibling;
  const isOpen = !tl.classList.contains('is-hidden');

  /* fecha irmãos */
  const parent = bar.parentElement;
  parent.querySelectorAll(':scope > .day-bar').forEach(b => {
    if (b === bar) return;
    const t = b.nextElementSibling;
    if (t && t.classList.contains('day-timeline') && !t.classList.contains('is-hidden')) {
      t.classList.add('is-hidden');
      b.querySelector('.day-chevron').style.transform = '';
      b.classList.remove('is-open');
    }
  });

  if (isOpen) {
    tl.classList.add('is-hidden');
    bar.querySelector('.day-chevron').style.transform = '';
    bar.classList.remove('is-open');
  } else {
    tl.classList.remove('is-hidden');
    bar.querySelector('.day-chevron').style.transform = 'rotate(180deg)';
    bar.classList.add('is-open');

    const c = tl.querySelector('.tl-container');
    if (c && !c.dataset.built) { buildTimeline(c); c.dataset.built = '1'; }

    requestAnimationFrame(() => autoScroll(tl));
  }
}

/* ═══════════════════════════════════════════
   BUILD TIMELINE
═══════════════════════════════════════════ */
function buildTimeline(container) {
  const els  = container.querySelectorAll('.tl-apt');
  const apts = Array.from(els).map(e => ({
    id: e.dataset.id,
    h: +e.dataset.h,  m: +e.dataset.m,  dur: +e.dataset.dur,
    svc: e.dataset.svc, client: e.dataset.client,
    total: e.dataset.total, time: e.dataset.time,
    status: e.dataset.status, obs: e.dataset.obs
  })).filter(a => !isNaN(a.h) && !isNaN(a.m));

  apts.sort((a, b) => (a.h * 60 + a.m) - (b.h * 60 + b.m));

  const totalPx = (TL_TO - TL_FROM) * TL_HH;

  const wrap = el('div', 'tl-wrap');
  wrap.style.height = totalPx + 'px';

  const hCol = el('div', 'tl-hours');
  hCol.style.height = totalPx + 'px';
  hCol.style.minHeight = totalPx + 'px';
  for (let h = TL_FROM; h <= TL_TO; h++) {
    const lbl = el('div', 'tl-hour-lbl');
    lbl.style.top = ((h - TL_FROM) * TL_HH) + 'px';
    lbl.textContent = String(h).padStart(2, '0') + ':00';
    hCol.appendChild(lbl);
  }

  /* track */
  const track = el('div', 'tl-track');
  track.style.height = totalPx + 'px';
  track.style.minHeight = totalPx + 'px';

  /* grid */
  for (let h = TL_FROM; h <= TL_TO; h++) {
    const y = (h - TL_FROM) * TL_HH;
    track.appendChild(gridLine(y));
    if (h < TL_TO) track.appendChild(gridLine(y + TL_HH / 2, true));
  }

  /* indicador "agora" */
  const dayStr  = container.dataset.day;
  const now     = new Date();
  const today   = fmt(now);
  if (dayStr === today) {
    const nEl = el('div', 'tl-now');
    nEl.style.top = ((now.getHours() * 60 + now.getMinutes()) / 60 * TL_HH) + 'px';
    track.appendChild(nEl);
  }

  /* blocos */
  let totalVal = 0;
  apts.forEach(a => {
    totalVal += parseFloat(a.total) || 0;

    const top  = ((a.h - TL_FROM) * 60 + a.m) / 60 * TL_HH;
    const raw  = a.dur / 60 * TL_HH;
    const h    = Math.max(raw, 30);
    const mini = raw < 44;

    const blk = el('div', 'tl-block tl-block--' + a.status + (mini ? ' tl-block--compact' : ''));
    blk.style.top    = top + 'px';
    blk.style.height = h + 'px';

    if (a.id && typeof APPOINTMENT_DETAIL_URL !== 'undefined') {
      blk.setAttribute('hx-get', APPOINTMENT_DETAIL_URL.replace('__ID__', a.id));
      blk.setAttribute('hx-target', '#appointment-modal-root');
      blk.setAttribute('hx-swap', 'innerHTML');
    }

    if (mini) {
      blk.innerHTML =
        span('tl-b-time', a.time) +
        span('tl-b-svc', esc(a.svc)) +
        (a.client ? span('tl-b-client', '· ' + esc(a.client)) : '');
    } else {
      blk.innerHTML =
        '<div class="tl-b-time">' + a.time + ' · ' + a.dur + 'min</div>' +
        '<div class="tl-b-svc">' + esc(a.svc) + '</div>' +
        (a.client ? '<div class="tl-b-client"><i class="fa-solid fa-user" style="font-size:9px;margin-right:4px;opacity:.5"></i>' + esc(a.client) + '</div>' : '') +
        (h >= 75  ? '<div class="tl-b-price">R$ ' + a.total + '</div>' : '') +
        (h >= 100 && a.obs ? '<div class="tl-b-obs"><i class="fa-regular fa-comment" style="font-size:9px;margin-right:4px;opacity:.5"></i>' + esc(a.obs) + '</div>' : '');
    }
    track.appendChild(blk);
    if (typeof htmx !== 'undefined') htmx.process(blk);
  });

  wrap.appendChild(hCol);
  wrap.appendChild(track);
  container.appendChild(wrap);

  /* total no header */
  const totEl = container.closest('.day-timeline').querySelector('.day-tl-total');
  if (totEl && totalVal > 0) {
    totEl.textContent = 'R$ ' + totalVal.toFixed(2).replace('.', ',');
    totEl.classList.add('has-value');
  }
}

/* ═══════════════════════════════════════════
   AUTO-SCROLL
═══════════════════════════════════════════ */
function autoScroll(wrap) {
  const sc = wrap.querySelector('.day-tl-scroll');
  if (!sc) return;
  const target = sc.querySelector('.tl-now') || sc.querySelector('.tl-block');
  if (target) sc.scrollTop = Math.max(0, parseInt(target.style.top) - 80);
}

/* ═══════════════════════════════════════════
   HELPERS
═══════════════════════════════════════════ */
function el(tag, cls)  { const e = document.createElement(tag); if (cls) e.className = cls; return e; }
function span(c, txt)  { return '<span class="' + c + '">' + txt + '</span>'; }
function gridLine(y, half) { const d = el('div', 'tl-grid' + (half ? ' tl-grid-half' : '')); d.style.top = y + 'px'; return d; }
function fmt(d) { return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }