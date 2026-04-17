/* ─────────────────────────────────────────
   Estado mínimo: só o que não vive no DOM
───────────────────────────────────────── */
var MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
             'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
var SEMANA = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];

var hoje = new Date(); hoje.setHours(0,0,0,0);
var calMes = hoje.getMonth();
var calAno = hoje.getFullYear();

var CONFIG_BARBEIRO    = {};   // {hora_inicio, hora_fim, interval_time}
var AGENDAMENTOS_DIA   = {};   // {date: [{inicio, fim}]}
var MESES_DISPONIVEIS  = [];
var duracaoTotalMin    = 0;

/* ── UTILITÁRIOS DE TEMPO ────────────────────────────────────────────────── */

/** "HH:MM" → minutos desde meia-noite */
function toMin(hhmm) {
  var p = hhmm.split(':');
  return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
}

/** minutos desde meia-noite → "HH:MM" */
function toHHMM(min) {
  var h = Math.floor(min / 60);
  var m = min % 60;
  return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
}

/* ── GERAÇÃO DINÂMICA DE SLOTS ───────────────────────────────────────────────
   Para cada passo do intervalo (ex: a cada 30 min), verifica se o serviço
   selecionado (duracaoTotalMin) cabe no espaço livre até o próximo agendamento.

   Um slot [inicio, inicio+duracao) é VÁLIDO se não sobrepõe nenhum
   agendamento existente [ag.inicio, ag.fim).
─────────────────────────────────────────────────────────────────────────────*/
function gerarSlotsDisponiveis(dateKey) {
  if (!CONFIG_BARBEIRO.hora_inicio) return [];

  var inicioMin   = toMin(CONFIG_BARBEIRO.hora_inicio);
  var fimMin      = toMin(CONFIG_BARBEIRO.hora_fim);
  var intervalo   = CONFIG_BARBEIRO.interval_time || 30;
  var duracao     = duracaoTotalMin > 0 ? duracaoTotalMin : intervalo;

  var agendamentos = (AGENDAMENTOS_DIA[dateKey] || []).map(function(ag) {
    return { inicio: toMin(ag.inicio), fim: toMin(ag.fim) };
  });

  var slots = [];

  for (var cursor = inicioMin; cursor + duracao <= fimMin; cursor += intervalo) {
    var slotInicio = cursor;
    var slotFim    = cursor + duracao;

    var livre = agendamentos.every(function(ag) {
      return slotFim <= ag.inicio || slotInicio >= ag.fim;
    });

    if (livre) {
      slots.push(toHHMM(slotInicio));
    }
  }

  return slots;
}

/* ── MODAL ── */
function openModal(id)  { document.getElementById(id).classList.add('open');    document.body.style.overflow='hidden'; }
function closeModal(id) { document.getElementById(id).classList.remove('open'); document.body.style.overflow=''; }
function closeOnBg(e,id){ if (e.target===e.currentTarget) closeModal(id); }

/* ── ESTADO DO CALENDÁRIO ── */
function calendarReady() {
  return !!(document.getElementById('h-barber-id').value &&
            document.getElementById('h-services').value);
}

function atualizarEstadoCalendario() {
  var overlay = document.getElementById('cal-overlay');
  if (!overlay) {
    injetarOverlayCalendario();
    overlay = document.getElementById('cal-overlay');
  }
  if (!overlay) return;

  if (calendarReady()) {
    overlay.style.display = 'none';
  } else {
    overlay.style.display = 'flex';
    document.getElementById('h-date').value          = '';
    document.getElementById('h-time').value          = '';
    document.getElementById('sum-date').textContent   = '—';
    document.getElementById('sum-time').textContent   = '—';
    document.getElementById('time-container').innerHTML =
      '<p class="time-empty">Selecione uma data para ver os horários</p>';
    renderCalendar();
    checkConfirm();
  }
}

/* ── BARBEIRO ── */
function selectBarber(el) {
  document.querySelectorAll('.barber-option').forEach(function(c){ c.classList.remove('selected'); });
  el.classList.add('selected');

  var barberId = el.dataset.id;

  document.getElementById('h-barber-id').value         = barberId;
  document.getElementById('barber-display').textContent = el.dataset.name;
  document.getElementById('barber-display').className   = 'trigger-value';
  document.getElementById('btn-barber').classList.add('filled');
  document.getElementById('sum-barber').textContent     = el.dataset.name;
  document.getElementById('btn-ok-barber').disabled     = false;

  CONFIG_BARBEIRO   = CONFIG_POR_BARBEIRO[barberId]       || {};
  AGENDAMENTOS_DIA  = AGENDAMENTOS_POR_BARBEIRO[barberId] || {};
  MESES_DISPONIVEIS = MESES_DISPONIVEIS_POR_BARBEIRO[barberId] || [];

  calMes = hoje.getMonth();
  calAno = hoje.getFullYear();
  if (MESES_DISPONIVEIS.length && !mesPermitido(calAno, calMes)) {
    calMes = MESES_DISPONIVEIS[0].mes - 1;
    calAno = MESES_DISPONIVEIS[0].ano;
  }

  document.getElementById('h-date').value          = '';
  document.getElementById('h-time').value          = '';
  document.getElementById('sum-date').textContent   = '—';
  document.getElementById('sum-time').textContent   = '—';
  document.getElementById('time-container').innerHTML =
    '<p class="time-empty">Selecione uma data para ver os horários</p>';
  renderCalendar();

  renderServiceList(SERVICOS_POR_BARBEIRO[barberId] || []);

  duracaoTotalMin = 0;
  document.getElementById('h-services').value           = '';
  document.getElementById('h-total').value              = '0';
  document.getElementById('service-display').className   = 'trigger-placeholder';
  document.getElementById('service-display').textContent = 'Selecionar serviços';
  document.getElementById('btn-service').classList.remove('filled');
  document.getElementById('sum-service').textContent     = '—';
  document.getElementById('sum-total').textContent       = 'R$0,00';
  document.getElementById('btn-ok-service').disabled     = true;

  atualizarEstadoCalendario();
}

/* ── SERVIÇOS ── */
function renderServiceList(servicos) {
  var list = document.querySelector('.service-list');
  list.innerHTML = '';

  if (!servicos.length) {
    list.innerHTML = '<p class="time-empty">Nenhum serviço disponível para este barbeiro</p>';
    return;
  }

  servicos.forEach(function(s) {
    var div = document.createElement('div');
    div.className       = 'service-option';
    div.dataset.id      = s.id;
    div.dataset.name    = s.nome;
    div.dataset.price   = s.preco;
    div.dataset.duracao = s.duracao;
    div.innerHTML =
      '<div class="svc-left">' +
        '<div class="svc-icon"><i class="fa-solid fa-scissors"></i></div>' +
        '<div>' +
          '<div class="svc-name">' + s.nome + '</div>' +
          '<div class="svc-time"><i class="fa-regular fa-clock"></i> ' + s.duracao + ' min</div>' +
        '</div>' +
      '</div>' +
      '<div class="svc-right">' +
        '<div class="svc-price">R$' + s.preco + '</div>' +
        '<div class="svc-check"><i class="fa-solid fa-check"></i></div>' +
      '</div>';
    div.addEventListener('click', function(){ toggleService(div); });
    list.appendChild(div);
  });
}

function toggleService(el) {
  var jaSelecionado = el.classList.contains('selected');

  document.querySelectorAll('.service-option').forEach(function(c){
    c.classList.remove('selected');
  });

  if (!jaSelecionado) {
    el.classList.add('selected');
  }

  recalcServices();
}

function recalcServices() {
  var ids=[], names=[], total=0, duracao=0;
  document.querySelectorAll('.service-option.selected').forEach(function(el){
    ids.push(el.dataset.id);
    names.push(el.dataset.name);
    total   += parseFloat(el.dataset.price)    || 0;
    duracao += parseInt(el.dataset.duracao, 10) || 0;
  });

  duracaoTotalMin = duracao;

  document.getElementById('h-services').value = ids.join(',');
  document.getElementById('h-total').value    = total.toFixed(2);

  var disp = document.getElementById('service-display');
  var btn  = document.getElementById('btn-service');
  if (names.length) {
    btn.classList.add('filled');
    disp.className = 'trigger-tags';
    disp.innerHTML = names.map(function(n){ return '<span class="tag">'+n+'</span>'; }).join('');
  } else {
    btn.classList.remove('filled');
    disp.className   = 'trigger-placeholder';
    disp.textContent = 'Selecionar serviços';
  }

  document.getElementById('sum-service').textContent =
    names.length ? names.join(', ') + ' (' + duracao + ' min)' : '—';
  document.getElementById('sum-total').textContent =
    'R$' + total.toFixed(2).replace('.', ',');
  document.getElementById('btn-ok-service').disabled = names.length === 0;

  var dataSel = document.getElementById('h-date').value;
  if (dataSel) {
    var slots = gerarSlotsDisponiveis(dataSel);
    renderSlots(slots);

    var timeSel = document.getElementById('h-time').value;
    if (timeSel && slots.indexOf(timeSel) === -1) {
      document.getElementById('h-time').value        = '';
      document.getElementById('sum-time').textContent = '—';
    }
  }

  renderCalendar();

  atualizarEstadoCalendario();
  checkConfirm();
}

/* ── CALENDÁRIO ── */
function mesPermitido(ano, mes) {
  return MESES_DISPONIVEIS.some(function(m){ return m.ano===ano && m.mes===(mes+1); });
}

function renderCalendar() {
  document.getElementById('cal-month-label').textContent = MESES[calMes].toUpperCase()+' '+calAno;

  var grid  = document.getElementById('cal-days');
  grid.innerHTML = '';
  var first = new Date(calAno, calMes, 1).getDay();
  var dias  = new Date(calAno, calMes+1, 0).getDate();

  for (var i=0; i<first; i++) {
    var vazio = document.createElement('div');
    vazio.className = 'cal-day empty';
    grid.appendChild(vazio);
  }

  var selDate = document.getElementById('h-date').value;

  for (var d=1; d<=dias; d++) {
    var el  = document.createElement('div');
    var dt  = new Date(calAno, calMes, d); dt.setHours(0,0,0,0);
    var key = dt.toISOString().slice(0,10);

    el.className   = 'cal-day';
    el.textContent = d;

    var passado = dt < hoje;
    var domingo = dt.getDay() === 0;

    var semSlot = false;
    if (calendarReady()) {
      semSlot = gerarSlotsDisponiveis(key).length === 0;
    }

    if (passado || domingo || semSlot) {
      el.classList.add('past');
    } else {
      if (dt.getTime() === hoje.getTime()) el.classList.add('today');
      el.dataset.key     = key;
      el.dataset.label   = SEMANA[dt.getDay()]+', '+d+' de '+MESES[calMes];
      el.dataset.dateIso = key;
      el.addEventListener('click', onDayClick);
    }

    if (selDate && selDate === key) el.classList.add('selected');

    grid.appendChild(el);
  }
}

function onDayClick() {
  if (!calendarReady()) return;

  document.getElementById('h-date').value         = this.dataset.dateIso;
  document.getElementById('h-time').value         = '';
  document.getElementById('sum-date').textContent  = this.dataset.label;
  document.getElementById('sum-time').textContent  = '—';

  renderCalendar(); // ← re-renderiza lendo h-date já atualizado, marca só o dia correto
  renderSlots(gerarSlotsDisponiveis(this.dataset.key));
  checkConfirm();
}

function changeMonth(dir) {
  var novoMes = calMes + dir;
  var novoAno = calAno;
  if (novoMes > 11) { novoMes = 0;  novoAno++; }
  if (novoMes < 0)  { novoMes = 11; novoAno--; }
  if (!mesPermitido(novoAno, novoMes)) return;
  calMes = novoMes; calAno = novoAno;
  renderCalendar();
}

/* ── SLOTS DE HORÁRIO ── */
function renderSlots(slots) {
  var c = document.getElementById('time-container');
  if (!slots.length) {
    c.innerHTML = '<p class="time-empty">Nenhum horário disponível neste dia</p>';
    return;
  }
  var grid = document.createElement('div');
  grid.className = 'time-grid';
  var selTime = document.getElementById('h-time').value;
  slots.forEach(function(t) {
    var el = document.createElement('div');
    el.className   = 'time-slot';
    el.textContent = t;
    if (selTime === t) el.classList.add('selected');
    el.addEventListener('click', function(){ selectTime(t, el); });
    grid.appendChild(el);
  });
  c.innerHTML = '';
  c.appendChild(grid);
}

function selectTime(t, el) {
  document.querySelectorAll('.time-slot').forEach(function(c){ c.classList.remove('selected'); });
  el.classList.add('selected');
  document.getElementById('h-time').value         = t;
  document.getElementById('sum-time').textContent  = t;
  checkConfirm();
}

/* ── VALIDAÇÃO & SUBMIT ── */
function checkConfirm() {
  var ok = document.getElementById('h-barber-id').value &&
           document.getElementById('h-services').value  &&
           document.getElementById('h-date').value      &&
           document.getElementById('h-time').value      &&
           document.getElementById('nome').value.trim() &&
           document.getElementById('telefone').value.trim();
  document.getElementById('btn-confirm').disabled = !ok;
}

function confirmar() {
  document.getElementById('h-nome').value     = document.getElementById('nome').value.trim();
  document.getElementById('h-telefone').value = document.getElementById('telefone').value.trim();
  document.getElementById('h-obs').value      = document.getElementById('obs').value.trim();
  document.getElementById('form-agendamento').submit();
}

/* ── MODAL DE RETORNO ── */
document.addEventListener('DOMContentLoaded', function() {
  injetarOverlayCalendario();
  atualizarEstadoCalendario();

  if (BOOKING_SUCCESS) {
    if (BOOKING_SUCCESS.status === 'success') {
      document.getElementById('title-id-form').textContent    = BOOKING_SUCCESS.title;
      document.getElementById('message-id-form').textContent  = BOOKING_SUCCESS.message;
      document.getElementById('horario-id-form').textContent  = BOOKING_SUCCESS.horario;
      openModal('modal-form-success');
    } else {
      document.getElementById('title-id-form-error').textContent   = BOOKING_SUCCESS.title;
      document.getElementById('message-id-form-error').textContent = BOOKING_SUCCESS.message;
      openModal('modal-form-error');
    }
  }
});

/* ── OVERLAY DO CALENDÁRIO ── */
function injetarOverlayCalendario() {
  if (document.getElementById('cal-overlay')) return;

  var calCard = document.querySelector('.cal-weekdays');
  if (!calCard) return;
  var cardPai = calCard.closest('.card');
  if (!cardPai) return;

  cardPai.style.position = 'relative';

  var ov = document.createElement('div');
  ov.id = 'cal-overlay';
  ov.innerHTML =
    '<div style="display:flex;flex-direction:column;align-items:center;gap:12px;padding:24px;text-align:center;">' +
      '<i class="fa-solid fa-lock" style="font-size:2rem;color:#c8a96e;opacity:.9;"></i>' +
      '<p style="color:#e8e0d5;font-size:.9rem;line-height:1.5;max-width:220px;margin:0;">' +
        'Selecione o <strong>barbeiro</strong> e pelo menos um <strong>serviço</strong> para ver os horários disponíveis' +
      '</p>' +
    '</div>';
  ov.style.cssText =
    'position:absolute;inset:0;z-index:10;display:flex;align-items:center;' +
    'justify-content:center;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);' +
    'background:rgba(0,0,0,0.55);border-radius:16px;';

  cardPai.appendChild(ov);
}

/* ── MODAL SERVIÇOS ── */
function abrirModalServicos() {
  if (!document.getElementById('h-barber-id').value) {
    alert('Selecione um barbeiro primeiro.');
    return;
  }
  openModal('modal-service');
}

function maskTelefone(input) {
  // pega só números
  var value = input.value.replace(/\D/g, '');

  // limita em 11 dígitos (Brasil)
  value = value.substring(0, 11);

  if (value.length <= 10) {
    // telefone fixo: (99) 9999-9999
    value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
    value = value.replace(/(\d{4})(\d)/, '$1-$2');
  } else {
    // celular: (99) 99999-9999
    value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
    value = value.replace(/(\d{5})(\d)/, '$1-$2');
  }

  input.value = value;
}

function maskCNPJ(input) {
    let value = input.value.replace(/\D/g, "");

    // limita a 14 dígitos
    value = value.substring(0, 14);

    // aplica a máscara
    value = value.replace(/^(\d{2})(\d)/, "$1.$2");
    value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
    value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
    value = value.replace(/(\d{4})(\d)/, "$1-$2");

    input.value = value;
}

(function () {
  var popup = document.getElementById("feedback-popup");
  var timer = null;

  if (popup && popup.parentElement !== document.body) {
    document.body.appendChild(popup);
  }

  function showPopup(type, message) {
    if (!popup || !message) return;

    popup.className = "feedback-popup " + (type || "error");
    popup.textContent = message;
    popup.classList.add("is-visible");

    clearTimeout(timer);
    timer = setTimeout(function () {
      popup.classList.remove("is-visible");
    }, 3500);
  }

  // Evento disparado automaticamente pelo HX-Trigger
  document.body.addEventListener("notify", function (evt) {
    var detail = evt.detail || {};
    showPopup(detail.type, detail.message);
  });
})();

/* ── INIT ── */
renderCalendar();
