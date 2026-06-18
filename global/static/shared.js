/* Utilitários compartilhados (admin + cliente) */
function pad(n) {
  return n < 10 ? '0' + n : String(n);
}

function openModal(id) {
  var el = document.getElementById(id);
  if (!el) return;
  el.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  var el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('open');
  document.body.style.overflow = '';
}

function closeOnBg(e, id) {
  if (e.target === e.currentTarget) closeModal(id);
}

function onlyDigits(value, max) {
  return value.replace(/\D/g, '').substring(0, max);
}

function maskTelefone(input) {
  var value = onlyDigits(input.value, 11);
  if (value.length <= 10) {
    value = value.replace(/^(\d{2})(\d)/g, '($1) $2').replace(/(\d{4})(\d)/, '$1-$2');
  } else {
    value = value.replace(/^(\d{2})(\d)/g, '($1) $2').replace(/(\d{5})(\d)/, '$1-$2');
  }
  input.value = value;
}

function maskCEP(input) {
  input.value = onlyDigits(input.value, 8).replace(/^(\d{5})(\d)/, '$1-$2');
}

function copyPortalLink(btn) {
  var link = btn.dataset.link || (document.getElementById('portal-link-input') || {}).value;
  if (!link) return;

  navigator.clipboard.writeText(link).then(function() {
    var span = btn.querySelector('span');
    if (!span) return;
    var original = span.textContent;
    span.textContent = 'Copiado!';
    setTimeout(function() { span.textContent = original; }, 2000);
  }).catch(function() {
    window.prompt('Copie o link:', link);
  });
}
