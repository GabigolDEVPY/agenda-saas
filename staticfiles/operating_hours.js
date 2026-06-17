(function buildHorariosFuncionamento() {
  var dias = [
    { key: 'dom', label: 'Domingo' },
    { key: 'seg', label: 'Segunda' },
    { key: 'ter', label: 'Terca' },
    { key: 'qua', label: 'Quarta' },
    { key: 'qui', label: 'Quinta' },
    { key: 'sex', label: 'Sexta' },
    { key: 'sab', label: 'Sabado' }
  ];

  var wrap = document.getElementById('horarios-funcionamento');
  if (!wrap) return;

  var defaults = operatingHours;
  var TIME_SLOTS = [];
  var h;
  for (h = 6; h <= 23; h++) {
    TIME_SLOTS.push(pad(h) + ':00');
    if (h < 23) TIME_SLOTS.push(pad(h) + ':30');
  }

  var activeDropdown = null;

  function closeActiveDropdown() {
    if (!activeDropdown) return;
    activeDropdown.style.display = 'none';
    activeDropdown = null;
  }

  document.addEventListener('click', function(e) {
    if (activeDropdown && !activeDropdown.contains(e.target) && !e.target.closest('.hf-time-btn')) {
      closeActiveDropdown();
    }
  });

  function submitRow(element, type) {
    var form = element.closest('.hf-row');
    if (!form) return;

    var typeInput = form.querySelector('[name="type"]');
    if (typeInput) typeInput.value = type;

    if (window.htmx) {
      htmx.trigger(form, 'submit');
      return;
    }
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  }

  function buildTimeDropdown(currentValue, hiddenInput, diaKey) {
    var drop = document.createElement('div');
    drop.className = 'hf-time-dropdown';

    TIME_SLOTS.forEach(function(slot) {
      var opt = document.createElement('div');
      opt.className = 'hf-time-opt' + (slot === currentValue ? ' is-selected' : '');
      opt.textContent = slot;
      opt.addEventListener('click', function(e) {
        e.stopPropagation();
        hiddenInput.value = slot;
        hiddenInput.closest('.hf-time-wrap').querySelector('.hf-time-label').textContent = slot;
        closeActiveDropdown();
        if (typeof operatingHours !== 'undefined' && operatingHours[diaKey]) {
           if (hiddenInput.name === 'abertura') operatingHours[diaKey].abertura = slot;
           if (hiddenInput.name === 'fechamento') operatingHours[diaKey].fechamento = slot;
        }
        submitRow(hiddenInput, 'update_time');
      });
      drop.appendChild(opt);
    });

    return drop;
  }

  function buildTimeWrap(name, value, diaKey) {
    var timeWrap = document.createElement('div');
    timeWrap.className = 'hf-time-wrap';

    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = name;
    hidden.value = value;

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hf-time-btn';
    btn.innerHTML = '<span class="hf-time-label">' + value + '</span>' +
      '<i class="fa-solid fa-chevron-down hf-time-chevron"></i>';

    var drop = buildTimeDropdown(value, hidden, diaKey);
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var isOpen = drop.style.display === 'block';
      closeActiveDropdown();
      if (!isOpen) {
        drop.style.display = 'block';
        activeDropdown = drop;
        var selected = drop.querySelector('.hf-time-opt.is-selected');
        if (selected) selected.scrollIntoView({ block: 'center' });
      }
    });

    timeWrap.appendChild(btn);
    timeWrap.appendChild(hidden);
    timeWrap.appendChild(drop);
    return timeWrap;
  }

  dias.forEach(function(dia) {
    var d = defaults[dia.key];
    var row = document.createElement('form');
    row.className = 'hf-row';
    row.setAttribute('hx-post', '/establishment/operating/day-alter');
    row.setAttribute('hx-swap', 'none');
    row.innerHTML =
      '<input type="hidden" name="csrfmiddlewaretoken" value="' + wrap.dataset.csrf + '">' +
      '<input type="hidden" name="day" value="' + dia.key + '">' +
      '<input type="hidden" name="type" value="">' +
      '<div class="hf-day-label">' + dia.label + '</div>' +
      '<label class="toggle hf-toggle">' +
        '<input type="checkbox" id="hf-' + dia.key + '-aberto"' + (d.aberto ? ' checked' : '') + '/>' +
        '<span class="toggle-track"></span>' +
      '</label>';

    var timesEl = document.createElement('div');
    timesEl.id = 'hf-' + dia.key + '-times';
    timesEl.className = 'hf-times' + (d.aberto ? '' : ' is-hidden');
    timesEl.appendChild(buildTimeWrap('abertura', d.abertura, dia.key));

    var sep = document.createElement('span');
    sep.className = 'hf-sep';
    sep.textContent = 'ate';
    timesEl.appendChild(sep);
    timesEl.appendChild(buildTimeWrap('fechamento', d.fechamento, dia.key));
    row.appendChild(timesEl);

    var closedEl = document.createElement('div');
    closedEl.id = 'hf-' + dia.key + '-closed';
    closedEl.className = 'hf-closed' + (d.aberto ? ' is-hidden' : '');
    closedEl.innerHTML = '<span class="badge badge-alert">Fechado</span>';
    row.appendChild(closedEl);

    row.querySelector('#hf-' + dia.key + '-aberto').addEventListener('change', function() {
      timesEl.classList.toggle('is-hidden', !this.checked);
      closedEl.classList.toggle('is-hidden', this.checked);
      if (typeof operatingHours !== 'undefined' && operatingHours[dia.key]) {
        operatingHours[dia.key].aberto = this.checked;
      }
      submitRow(this, 'update_day');
    });

    wrap.appendChild(row);
  });
})();
