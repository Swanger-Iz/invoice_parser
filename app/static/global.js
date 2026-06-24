// ── Nav: mark active link ──
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.getAttribute('href') === window.location.pathname) {
    link.classList.add('active');
  }
});

// ── Toast helper ──
function showToast(message, type = 'info', duration = 3500) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── API helper ──
async function apiFetch(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

// ── Format date ──
function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

// ════════════════════════════════════════════
// ── Global Task Widget ──
// Живёт поверх всех страниц, состояние в sessionStorage
// ════════════════════════════════════════════

const TASK_KEY  = 'invoice_task_id';
const START_KEY = 'invoice_task_start';

let _pollInterval  = null;
let _timerInterval = null;
let _widget        = null;

function _createWidget() {
  const el = document.createElement('div');
  el.id = 'globalTaskWidget';
  el.innerHTML = `
    <div class="gtw-header">
      <span class="label">фоновая задача</span>
      <span class="gtw-id label"></span>
    </div>
    <div class="gtw-processing">
      <div class="gtw-spinner"></div>
      <div>
        <p class="gtw-status-text">Обрабатывается…</p>
        <p class="gtw-status-sub">модель извлекает данные</p>
      </div>
    </div>
    <div class="gtw-timer-row">
      <span class="label">время</span>
      <span class="gtw-timer">0.0 с</span>
    </div>
    <div class="gtw-done" hidden>
      <span class="gtw-done-badge"></span>
      <p class="gtw-done-msg"></p>
    </div>
    <p class="gtw-countdown" hidden></p>
    <button class="gtw-dismiss btn btn-ghost">закрыть</button>
  `;
  document.body.appendChild(el);

  el.querySelector('.gtw-dismiss').addEventListener('click', () => {
    _stopGlobalPolling();
    sessionStorage.removeItem(TASK_KEY);
    sessionStorage.removeItem(START_KEY);
    el.remove();
    _widget = null;
  });

  return el;
}

function _updateTimer() {
  if (!_widget) return;
  const start = parseInt(sessionStorage.getItem(START_KEY) || Date.now());
  _widget.querySelector('.gtw-timer').textContent =
    ((Date.now() - start) / 1000).toFixed(1) + ' с';
}

function _setWidgetDone(status, detail) {
  if (!_widget) return;
  _widget.querySelector('.gtw-processing').hidden = true;
  _widget.querySelector('.gtw-timer-row').hidden  = true;

  const done  = _widget.querySelector('.gtw-done');
  const badge = done.querySelector('.gtw-done-badge');
  const msg   = done.querySelector('.gtw-done-msg');
  const countdown = _widget.querySelector('.gtw-countdown');

  if (status === 'success') {
    badge.innerHTML = '<span class="badge badge-green">✓ success</span>';
    msg.innerHTML   = 'Готово. <a href="/requests">Открыть запросы →</a>';
  } else {
    badge.innerHTML = '<span class="badge badge-red">✕ error</span>';
    msg.textContent = detail || 'Ошибка при обработке.';
    msg.style.color = 'var(--error)';
  }
  done.hidden = false;

  // Автозакрытие с обратным отсчётом
  let secs = 4;
  countdown.textContent = 'Закроется через ' + secs + ' с';
  countdown.hidden = false;
  const cd = setInterval(() => {
    secs--;
    if (secs <= 0) {
      clearInterval(cd);
      if (_widget) {
        _widget.remove();
        _widget = null;
      }
    } else {
      countdown.textContent = 'Закроется через ' + secs + ' с';
    }
  }, 1000);
}

async function _pollGlobal(taskId) {
  try {
    const data = await apiFetch(`/status/${taskId}`);
    const status = data.status?.status ?? data.status;

    if (status === 'success' || status === 'error') {
      _stopGlobalPolling();
      sessionStorage.removeItem(TASK_KEY);
      sessionStorage.removeItem(START_KEY);
      _setWidgetDone(status, data.status?.detail);
    }
  } catch (err) {
    console.warn('Global poll error:', err.message);
  }
}

function _stopGlobalPolling() {
  clearInterval(_pollInterval);
  clearInterval(_timerInterval);
  _pollInterval  = null;
  _timerInterval = null;
}

// Вызывается из recognize.js после получения task_id
function startGlobalTask(taskId) {
  sessionStorage.setItem(TASK_KEY,  taskId);
  sessionStorage.setItem(START_KEY, Date.now());
  _launchWidget(taskId);
}

function _launchWidget(taskId) {
  if (_widget) _widget.remove();
  _stopGlobalPolling();

  _widget = _createWidget();
  _widget.querySelector('.gtw-id').textContent = taskId.slice(0, 8) + '…';

  _timerInterval = setInterval(_updateTimer, 100);
  _pollInterval  = setInterval(() => _pollGlobal(taskId), 3000);
}

// При загрузке любой страницы — возобновляем незавершённую задачу
(function resumeIfNeeded() {
  const taskId = sessionStorage.getItem(TASK_KEY);
  if (taskId) _launchWidget(taskId);
})();