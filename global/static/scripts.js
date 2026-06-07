/* Portal do cliente — agendamento */
var MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
var SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

var hoje = new Date();
hoje.setHours(0, 0, 0, 0);

var calMes = hoje.getMonth();
var calAno = hoje.getFullYear();
var CONFIG_BARBEIRO = {};
var AGENDAMENTOS_DIA = {};
var MESES_DISPONIVEIS = [];
var duracaoTotalMin = 0;

function $(id) {
  return document.getElementById(id);
}

function toMin(hhmm) {
  var p = hhmm.split(':');
  return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
}

function toHHMM(min) {
  return pad(Math.floor(min / 60)) + ':' + pad(min % 60);
}

function toDateKey(dt) {
  return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate());
}

function isHoje(dateKey) {
  return dateKey === toDateKey(new Date());
}

function getAgoraMin() {
  var agora = new Date();
  return agora.getHours() * 60 + agora.getMinutes();
}

function filtrarHorariosPassados(dateKey, slots) {
  if (!isHoje(dateKey)) return slots;
  var agoraMin = getAgoraMin();
  return slots.filter(function(slot) {
    return toMin(slot) > agoraMin;
  });
}

function gerarSlotsDisponiveis(dateKey) {
  if (!CONFIG_BARBEIRO.hora_inicio) return [];

  var funcionamento = getFuncionamentoDoDia(dateKey);
  if (!funcionamento || !funcionamento.aberto) return [];

  var inicioMin = toMin(funcionamento.inicio);
  var fimMin = toMin(funcionamento.fim);
  var duracao = getDuracaoSelecionada();
  if (duracao <= 0) return [];

  if (isHoje(dateKey) && inicioMin <= getAgoraMin()) {
    var proximo = getAgoraMin() + 1;
    var resto = (proximo - inicioMin) % duracao;
    inicioMin = resto === 0 ? proximo : proximo + (duracao - resto);
  }

  var agendamentos = (AGENDAMENTOS_DIA[dateKey] || []).map(function(ag) {
    return { inicio: toMin(ag.inicio), fim: toMin(ag.fim) };
  });

  var candidatos = [];
  var cursor;
  for (cursor = inicioMin; cursor + duracao <= fimMin; cursor += duracao) {
    candidatos.push(cursor);
  }

  agendamentos.forEach(function(ag) {
    if (ag.fim >= inicioMin && ag.fim + duracao <= fimMin) candidatos.push(ag.fim);
  });

  candidatos = candidatos.filter(function(valor, indice, lista) {
    return lista.indexOf(valor) === indice;
  }).sort(function(a, b) {
    return a - b;
  });

  var slots = [];
  candidatos.forEach(function(slotInicio) {
    var slotFim = slotInicio + duracao;
    var livre = agendamentos.every(function(ag) {
      return slotFim <= ag.inicio || slotInicio >= ag.fim;
    });
    if (livre) slots.push(toHHMM(slotInicio));
  });

  return filtrarHorariosPassados(dateKey, slots);
}

function getDuracaoSelecionada() {
  var duracao = 0;
  document.querySelectorAll('.service-option.selected').forEach(function(el) {
    duracao += parseInt(el.dataset.duracao, 10) || 0;
  });
  return duracao > 0 ? duracao : duracaoTotalMin;
}

function getFuncionamentoDoDia(dateKey) {
  var horarios = CONFIG_BARBEIRO.horarios_funcionamento || {};
  if (dateKey) {
    var dia = String(new Date(dateKey + 'T00:00:00').getDay());
    if (horarios[dia]) return horarios[dia];
  }
  return {
    aberto: true,
    inicio: CONFIG_BARBEIRO.hora_inicio,
    fim: CONFIG_BARBEIRO.hora_fim
  };
}

function calendarReady() {
  return !!($('h-barber-id').value && $('h-services').value);
}

function limparSelecaoDataHorario() {
  $('h-date').value = '';
  $('h-time').value = '';
  $('sum-date').textContent = '—';
  $('sum-time').textContent = '—';
  $('time-container').innerHTML = '<p class="time-empty">Selecione uma data para ver os horários</p>';
}

function atualizarEstadoCalendario() {
  var overlay = $('cal-overlay');
  if (!overlay) {
    injetarOverlayCalendario();
    overlay = $('cal-overlay');
  }
  if (!overlay) return;

  if (calendarReady()) {
    overlay.style.display = 'none';
    return;
  }

  overlay.style.display = 'flex';
  limparSelecaoDataHorario();
  renderCalendar();
  checkConfirm();
}

function selectBarber(el) {
  document.querySelectorAll('.barber-option').forEach(function(item) {
    item.classList.remove('selected');
  });
  el.classList.add('selected');

  var barberId = el.dataset.id;
  $('h-barber-id').value = barberId;
  $('barber-display').textContent = el.dataset.name;
  $('barber-display').className = 'trigger-value';
  $('btn-barber').classList.add('filled');
  $('sum-barber').textContent = el.dataset.name;
  $('btn-ok-barber').disabled = false;

  CONFIG_BARBEIRO = CONFIG_POR_BARBEIRO[barberId] || {};
  AGENDAMENTOS_DIA = AGENDAMENTOS_POR_BARBEIRO[barberId] || {};
  MESES_DISPONIVEIS = MESES_DISPONIVEIS_POR_BARBEIRO[barberId] || [];

  calMes = hoje.getMonth();
  calAno = hoje.getFullYear();
  if (MESES_DISPONIVEIS.length && !mesPermitido(calAno, calMes)) {
    calMes = MESES_DISPONIVEIS[0].mes - 1;
    calAno = MESES_DISPONIVEIS[0].ano;
  }

  limparSelecaoDataHorario();
  renderCalendar();
  renderServiceList(SERVICOS_POR_BARBEIRO[barberId] || []);

  duracaoTotalMin = 0;
  $('h-services').value = '';
  $('h-total').value = '0';
  $('service-display').className = 'trigger-placeholder';
  $('service-display').textContent = 'Selecionar serviços';
  $('btn-service').classList.remove('filled');
  $('sum-service').textContent = '—';
  $('sum-total').textContent = 'R$0,00';
  $('btn-ok-service').disabled = true;
  atualizarEstadoCalendario();
}

function renderServiceList(servicos) {
  var list = document.querySelector('.service-list');
  if (!list) return;
  list.innerHTML = '';

  if (!servicos.length) {
    list.innerHTML = '<p class="time-empty">Nenhum serviço disponível para este profissional</p>';
    return;
  }

  var frag = document.createDocumentFragment();
  servicos.forEach(function(s) {
    var div = document.createElement('div');
    div.className = 'service-option';
    div.dataset.id = s.id;
    div.dataset.name = s.nome;
    div.dataset.price = s.preco;
    div.dataset.duracao = s.duracao;
    div.innerHTML =
      '<div class="svc-left">' +
        '<div class="svc-icon"><i class="fa-solid fa-scissors"></i></div>' +
        '<div><div class="svc-name">' + s.nome + '</div>' +
        '<div class="svc-time"><i class="fa-regular fa-clock"></i> ' + s.duracao + ' min</div></div>' +
      '</div>' +
      '<div class="svc-right"><div class="svc-price">R$' + s.preco + '</div>' +
      '<div class="svc-check"><i class="fa-solid fa-check"></i></div></div>';
    div.addEventListener('click', function() { toggleService(div); });
    frag.appendChild(div);
  });
  list.appendChild(frag);
}

function toggleService(el) {
  var selected = el.classList.contains('selected');
  document.querySelectorAll('.service-option').forEach(function(item) {
    item.classList.remove('selected');
  });
  if (!selected) el.classList.add('selected');
  recalcServices();
}

function recalcServices() {
  var ids = [];
  var names = [];
  var total = 0;
  var duracao = 0;

  document.querySelectorAll('.service-option.selected').forEach(function(el) {
    ids.push(el.dataset.id);
    names.push(el.dataset.name);
    total += parseFloat(el.dataset.price) || 0;
    duracao += parseInt(el.dataset.duracao, 10) || 0;
  });

  duracaoTotalMin = duracao;
  $('h-services').value = ids.join(',');
  $('h-total').value = total.toFixed(2);

  var disp = $('service-display');
  var btn = $('btn-service');
  if (names.length) {
    btn.classList.add('filled');
    disp.className = 'trigger-tags';
    disp.innerHTML = names.map(function(n) { return '<span class="tag">' + n + '</span>'; }).join('');
  } else {
    btn.classList.remove('filled');
    disp.className = 'trigger-placeholder';
    disp.textContent = 'Selecionar serviços';
  }

  $('sum-service').textContent = names.length ? names.join(', ') + ' (' + duracao + ' min)' : '—';
  $('sum-total').textContent = 'R$' + total.toFixed(2).replace('.', ',');
  $('btn-ok-service').disabled = names.length === 0;

  var dataSel = $('h-date').value;
  if (dataSel) {
    var slots = gerarSlotsDisponiveis(dataSel);
    renderSlots(slots);
    var timeSel = $('h-time').value;
    if (timeSel && slots.indexOf(timeSel) === -1) {
      $('h-time').value = '';
      $('sum-time').textContent = '—';
    }
  }

  renderCalendar();
  atualizarEstadoCalendario();
  checkConfirm();
}

function mesPermitido(ano, mes) {
  return MESES_DISPONIVEIS.some(function(m) {
    return m.ano === ano && m.mes === (mes + 1);
  });
}

function renderCalendar() {
  var grid = $('cal-days');
  if (!grid) return;

  $('cal-month-label').textContent = MESES[calMes].toUpperCase() + ' ' + calAno;
  grid.innerHTML = '';

  var first = new Date(calAno, calMes, 1).getDay();
  var dias = new Date(calAno, calMes + 1, 0).getDate();
  var selDate = $('h-date').value;
  var frag = document.createDocumentFragment();
  var i;
  var d;
  var el;
  var dt;
  var key;

  for (i = 0; i < first; i++) {
    el = document.createElement('div');
    el.className = 'cal-day empty';
    frag.appendChild(el);
  }

  for (d = 1; d <= dias; d++) {
    dt = new Date(calAno, calMes, d);
    dt.setHours(0, 0, 0, 0);
    key = toDateKey(dt);

    el = document.createElement('div');
    el.className = 'cal-day';
    el.textContent = d;

    if (dt < hoje || (calendarReady() && gerarSlotsDisponiveis(key).length === 0)) {
      el.classList.add('past');
    } else {
      if (dt.getTime() === hoje.getTime()) el.classList.add('today');
      el.dataset.key = key;
      el.dataset.label = SEMANA[dt.getDay()] + ', ' + d + ' de ' + MESES[calMes];
      el.dataset.dateIso = key;
    }

    if (selDate === key) el.classList.add('selected');
    frag.appendChild(el);
  }

  grid.appendChild(frag);
}

function onDayClick(dayEl) {
  if (!calendarReady() || !dayEl.dataset.key) return;

  $('h-date').value = dayEl.dataset.dateIso;
  $('h-time').value = '';
  $('sum-date').textContent = dayEl.dataset.label;
  $('sum-time').textContent = '—';

  renderCalendar();
  renderSlots(gerarSlotsDisponiveis(dayEl.dataset.key));
  checkConfirm();
}

function changeMonth(dir) {
  var novoMes = calMes + dir;
  var novoAno = calAno;
  if (novoMes > 11) { novoMes = 0; novoAno++; }
  if (novoMes < 0) { novoMes = 11; novoAno--; }
  if (!mesPermitido(novoAno, novoMes)) return;
  calMes = novoMes;
  calAno = novoAno;
  renderCalendar();
}

function renderSlots(slots) {
  var container = $('time-container');
  if (!container) return;

  if (!slots.length) {
    container.innerHTML = '<p class="time-empty">Nenhum horário disponível neste dia</p>';
    return;
  }

  var grid = document.createElement('div');
  grid.className = 'time-grid';
  var selTime = $('h-time').value;
  var frag = document.createDocumentFragment();

  slots.forEach(function(t) {
    var el = document.createElement('div');
    el.className = 'time-slot' + (selTime === t ? ' selected' : '');
    el.textContent = t;
    el.addEventListener('click', function() { selectTime(t, el); });
    frag.appendChild(el);
  });

  grid.appendChild(frag);
  container.innerHTML = '';
  container.appendChild(grid);
}

function selectTime(t, el) {
  document.querySelectorAll('.time-slot').forEach(function(item) {
    item.classList.remove('selected');
  });
  el.classList.add('selected');
  $('h-time').value = t;
  $('sum-time').textContent = t;
  checkConfirm();
}

function checkConfirm() {
  var btn = $('btn-confirm');
  if (!btn) return;
  btn.disabled = !(
    $('h-barber-id').value &&
    $('h-services').value &&
    $('h-date').value &&
    $('h-time').value &&
    $('nome').value.trim() &&
    $('telefone').value.trim()
  );
}

function confirmar() {
  $('h-nome').value = $('nome').value.trim();
  $('h-telefone').value = $('telefone').value.trim();
  $('h-obs').value = $('obs').value.trim();
  $('form-agendamento').submit();
}

function injetarOverlayCalendario() {
  if ($('cal-overlay')) return;

  var calCard = document.querySelector('.cal-weekdays');
  if (!calCard) return;
  var cardPai = calCard.closest('.card');
  if (!cardPai) return;

  cardPai.style.position = 'relative';
  var ov = document.createElement('div');
  ov.id = 'cal-overlay';
  ov.className = 'cal-overlay';
  ov.innerHTML =
    '<div class="cal-overlay-content">' +
      '<i class="fa-solid fa-lock cal-overlay-icon"></i>' +
      '<p>Selecione o <strong>profissional</strong> e pelo menos um <strong>serviço</strong> para ver os horários disponíveis</p>' +
    '</div>';
  cardPai.appendChild(ov);
}

function abrirModalServicos() {
  if (!$('h-barber-id').value) {
    alert('Selecione um profissional primeiro.');
    return;
  }
  openModal('modal-service');
}

function initBookingPage() {
  var calDays = $('cal-days');
  if (calDays) {
    calDays.addEventListener('click', function(e) {
      var day = e.target.closest('.cal-day:not(.past):not(.empty)');
      if (day) onDayClick(day);
    });
  }

  injetarOverlayCalendario();
  atualizarEstadoCalendario();

  if (typeof BOOKING_SUCCESS !== 'undefined' && BOOKING_SUCCESS) {
    if (BOOKING_SUCCESS.status === 'success') {
      $('title-id-form').textContent = BOOKING_SUCCESS.title;
      $('message-id-form').textContent = BOOKING_SUCCESS.message;
      $('horario-id-form').textContent = BOOKING_SUCCESS.horario;
      openModal('modal-form-success');
    } else {
      $('title-id-form-error').textContent = BOOKING_SUCCESS.title;
      $('message-id-form-error').textContent = BOOKING_SUCCESS.message;
      openModal('modal-form-error');
    }
  }
}

document.addEventListener('DOMContentLoaded', initBookingPage);
