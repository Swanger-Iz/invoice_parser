const tbody      = document.getElementById('requestsBody');
const detailCard = document.getElementById('detailCard');
const closeDetail= document.getElementById('closeDetail');

const detailId          = document.getElementById('detailId');
const detailConstructor = document.getElementById('detailConstructor');
const detailCustomer    = document.getElementById('detailCustomer');
const detailStatus      = document.getElementById('detailStatus');
const detailImage       = document.getElementById('detailImage');

// ── Load list ──
async function loadRequests() {
  try {
    const res = await fetch('/requests/');
    if (res.status === 404) {
      renderTable([]);
      return;
    }
    if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`);
    const rows = await res.json();
    renderTable(rows);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty">${err.message}</div></td></tr>`;
  }
}

function statusBadge(row) {
  const hasConstructor = !!row.constructor_name;
  const hasCustomer    = !!row.customer_name;
  if (hasConstructor && hasCustomer)
    return '<span class="badge badge-green">●</span>';
  if (hasConstructor || hasCustomer)
    return '<span class="badge badge-warn">●</span>';
  return '<span class="badge badge-red">●</span>';
}

function renderTable(rows) {
  if (!rows || rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty">Нет запросов. <a href="/recognize">Распознать документ →</a></div></td></tr>`;
    return;
  }

  tbody.innerHTML = rows.map(r => `
    <tr data-id="${r.id}">
      <td>${r.id}</td>
      <td>${r.constructor_name || '—'}</td>
      <td>${r.customer_name   || '—'}</td>
      <td>${statusBadge(r)}</td>
      <td><span class="label" style="cursor:pointer;color:var(--accent)">просмотр</span></td>
    </tr>
  `).join('');

  tbody.querySelectorAll('tr').forEach(tr => {
    tr.addEventListener('click', () => openDetail(tr.dataset.id));
  });
}

// ── Detail ──
async function openDetail(id) {
  detailCard.hidden = false;
  detailId.textContent = `#${id}`;
  detailConstructor.textContent = '…';
  detailCustomer.textContent    = '…';
  detailStatus.innerHTML        = '';
  detailImage.src               = '';

  try {
    const row = await apiFetch(`/requests/${id}`);
    detailConstructor.textContent = row.constructor_name || '—';
    detailCustomer.textContent    = row.customer_name    || '—';
    detailStatus.innerHTML        = statusBadge(row);
  } catch (err) {
    showToast(err.message, 'error');
  }

  // Load image — click opens in new tab
  const imageUrl = `/requests/${id}/image`;
  detailImage.src = imageUrl;
  detailImage.style.cursor = 'zoom-in';
  detailImage.onclick = () => window.open(imageUrl, '_blank');
  detailImage.onerror = () => { detailImage.alt = 'Изображение недоступно'; detailImage.style.cursor = 'default'; detailImage.onclick = null; };

  detailCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

closeDetail.addEventListener('click', () => {
  detailCard.hidden = true;
});

loadRequests();