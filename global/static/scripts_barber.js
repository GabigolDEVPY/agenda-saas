/* Admin — agenda, serviços e funcionários */
var DIAS_OFF = [];
var HORARIOS = {};

var DEFAULT_SLOTS = [];
(function() {
  var h;
  for (h = 9; h < 20; h++) {
    DEFAULT_SLOTS.push(pad(h) + ':00');
    DEFAULT_SLOTS.push(pad(h) + ':30');
  }
})();

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
    mState.dayData[d] = { off: false, slots: HORARIOS[d].slice() };
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

    data = mState.dayData[dateStr];
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
    mState.dayData[dateStr] = { off: false, slots: DEFAULT_SLOTS.slice() };
  }
  return mState.dayData[dateStr];
}

function renderTimeGrid(dateStr) {
  var grid = document.getElementById('m-time-grid');
  if (!grid) return;

  grid.innerHTML = '';
  var data = getDayData(dateStr);

  if (data.off) {
    grid.innerHTML = '<p class="m-day-off-msg"><i class="fa-solid fa-ban"></i> Dia marcado como folga — sem atendimentos.</p>';
    return;
  }

  var frag = document.createDocumentFragment();
  DEFAULT_SLOTS.forEach(function(slot) {
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
    data.off = false;
    data.slots = DEFAULT_SLOTS.slice();
    updateDayCalClass(mState.selectedDay, false);
  });
}

function setMorningOnly() {
  applyDaySlots(function(data) {
    data.off = false;
    data.slots = DEFAULT_SLOTS.filter(function(s) {
      return parseInt(s.split(':')[0], 10) < 12;
    });
  });
}

function setAfternoonOnly() {
  applyDaySlots(function(data) {
    data.off = false;
    data.slots = DEFAULT_SLOTS.filter(function(s) {
      return parseInt(s.split(':')[0], 10) >= 12;
    });
  });
}

function setAllSlots() {
  applyDaySlots(function(data) {
    data.off = false;
    data.slots = DEFAULT_SLOTS.slice();
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
    alreadyOpen = openedMonths.some(function(o) { return o.m === m && o.y === y; });

    item = document.createElement('div');
    item.className = 'month-pick-item';
    item.dataset.m = m;
    item.dataset.y = y;
    item.innerHTML =
      '<span>' + label + '</span>' +
      (alreadyOpen
        ? '<span class="month-pick-open"><i class="fa-solid fa-check"></i>Aberta</span>'
        : '<i class="fa-solid fa-chevron-right month-pick-arrow"></i>');

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

buildPickMonthList();
buildDefaultHoursCard();
