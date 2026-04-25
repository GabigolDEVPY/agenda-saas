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

  var defaults = operatingHours
  console.log(defaults)

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
      RequestChangeDay(dia.key)
    });

    wrap.appendChild(row);
  });
})();



function RequestChangeDay(dayKey) {
  // Função interna pra pegar o CSRF do cookie
  function getCSRFToken() {
    let cookieValue = null;
    const cookies = document.cookie.split(';');

    cookies.forEach(cookie => {
      const c = cookie.trim();
      if (c.startsWith('csrftoken=')) {
        cookieValue = c.substring('csrftoken='.length);
      }
    });

    return cookieValue;
  }

  var aberto    = document.getElementById('hf-' + dayKey + '-aberto').checked;
  var abertura  = document.querySelector('[name="hf_' + dayKey + '_abertura"]')?.value;
  var fechamento = document.querySelector('[name="hf_' + dayKey + '_fechamento"]')?.value;

  fetch('/establishment/operating/day-alter', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      day: dayKey,
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log(data.message)
      showToast(data.message);
    }
  })
  .catch(err => console.error('Erro ao atualizar:', err));
}


