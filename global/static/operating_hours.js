(function buildHorariosFuncionamento() {
  var dias = [
    { key: 'dom', label: 'Domingo' },
    { key: 'seg', label: 'Segunda' },
    { key: 'ter', label: 'Terca' },
    { key: 'qua', label: 'Quarta' },
    { key: 'qui', label: 'Quinta' },
    { key: 'sex', label: 'Sexta' },
    { key: 'sab', label: 'Sabado' },
  ];

  var defaults = operatingHours;
  var wrap = document.getElementById('horarios-funcionamento');
  if (!wrap) return;

  var TIME_SLOTS = [];
  for (var h = 6; h <= 23; h++) {
    TIME_SLOTS.push(pad(h) + ':00');
    if (h < 23) TIME_SLOTS.push(pad(h) + ':30');
  }

  var activeDropdown = null;

  function closeActiveDropdown() {
    if (activeDropdown) {
      activeDropdown.style.display = 'none';
      activeDropdown = null;
    }
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

  function buildTimeDropdown(currentValue, hiddenInput) {
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
        hiddenInput.value = slot;
        hiddenInput.closest('.hf-time-wrap').querySelector('.hf-time-label').textContent = slot;
        closeActiveDropdown();
        submitRow(hiddenInput, 'update_time');
      });

      drop.appendChild(opt);
    });

    return drop;
  }

  function buildTimeWrap(name, value) {
    var timeWrap = document.createElement('div');
    timeWrap.className = 'hf-time-wrap';
    timeWrap.style.cssText = 'position:relative;display:inline-block;';

    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = name;
    hidden.value = value;

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hf-time-btn';
    btn.style.cssText = 'display:flex;align-items:center;gap:6px;padding:6px 12px;' +
      'background:var(--surface2,#242424);border:1px solid var(--border,#333);border-radius:6px;' +
      'color:var(--text,#fff);font-size:13px;font-family:monospace;cursor:pointer;transition:border-color .2s;';
    btn.innerHTML = '<span class="hf-time-label">' + value + '</span>' +
      '<i class="fa-solid fa-chevron-down" style="font-size:10px;opacity:.6;"></i>';

    btn.addEventListener('mouseenter', function() { this.style.borderColor = 'var(--gold,#c9a84c)'; });
    btn.addEventListener('mouseleave', function() { this.style.borderColor = 'var(--border,#333)'; });

    var drop = buildTimeDropdown(value, hidden);
    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var isOpen = drop.style.display !== 'none';
      closeActiveDropdown();
      if (!isOpen) {
        drop.style.display = 'block';
        activeDropdown = drop;
        var selected = drop.querySelector('.hf-time-opt[style*="gold"]');
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
      '<label class="toggle" style="flex-shrink:0;">' +
        '<input type="checkbox" id="hf-' + dia.key + '-aberto"' + (d.aberto ? ' checked' : '') + '/>' +
        '<span class="toggle-track"></span>' +
      '</label>';

    var timesEl = document.createElement('div');
    timesEl.id = 'hf-' + dia.key + '-times';
    timesEl.className = 'hf-times';
    timesEl.style.display = d.aberto ? 'flex' : 'none';
    timesEl.style.alignItems = 'center';
    timesEl.style.gap = '15px';
    timesEl.appendChild(buildTimeWrap('abertura', d.abertura));

    var sep = document.createElement('span');
    sep.className = 'hf-sep';
    sep.textContent = 'ate';
    timesEl.appendChild(sep);

    timesEl.appendChild(buildTimeWrap('fechamento', d.fechamento));
    row.appendChild(timesEl);

    var closedEl = document.createElement('div');
    closedEl.id = 'hf-' + dia.key + '-closed';
    closedEl.style.cssText = 'display:' + (d.aberto ? 'none' : 'flex') + ';align-items:center;';
    closedEl.innerHTML = '<span class="badge badge-alert">Fechado</span>';
    row.appendChild(closedEl);

    var checkbox = row.querySelector('#hf-' + dia.key + '-aberto');
    checkbox.addEventListener('change', function() {
      timesEl.style.display = this.checked ? 'flex' : 'none';
      closedEl.style.display = this.checked ? 'none' : 'flex';
      submitRow(this, 'update_day');
    });

    wrap.appendChild(row);
  });
})();
