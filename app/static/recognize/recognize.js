const fileInput          = document.getElementById('fileInput');
const dropZone           = document.getElementById('dropZone');
const previewWrap        = document.getElementById('previewWrap');
const previewImg         = document.getElementById('previewImg');
const previewPlaceholder = document.getElementById('previewPlaceholder');
const previewName        = document.getElementById('previewName');
const clearBtn           = document.getElementById('clearBtn');
const submitBtn          = document.getElementById('submitBtn');
const uploadCard         = document.getElementById('uploadCard');

let selectedFile = null;

// ── File select ──
fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));

// ── Drag & Drop ──
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['jpg', 'jpeg', 'png'].includes(ext)) {
    showToast('Допустимые форматы: JPG, JPEG, PNG', 'error');
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    showToast('Файл превышает 20 МБ', 'error');
    return;
  }
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    previewImg.style.display = 'block';
    previewPlaceholder.style.display = 'none';
    previewName.textContent = file.name;
    dropZone.hidden = true;
    previewWrap.hidden = false;
    submitBtn.disabled = false;
  };
  reader.readAsDataURL(file);
}

// ── Clear ──
clearBtn.addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  previewImg.src = '';
  previewImg.style.display = 'none';
  previewName.textContent = '';
  previewPlaceholder.style.display = 'flex';
  dropZone.hidden = false;
  previewWrap.hidden = true;
  submitBtn.disabled = true;
});

// ── Submit ──
submitBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append('upload_file', selectedFile);
  submitBtn.disabled = true;

  try {
    const res = await fetch('/api/v1/get_fio', { method: 'POST', body: formData });
    const data = await res.json();

    // Cache hit (200) — сразу в историю
    if (res.status === 200 || data.constructor_name !== undefined) {
      showToast('Результат получен из кэша', 'success');
      window.location.href = '/requests';
      return;
    }

    // Background task (202) — запускаем глобальный виджет
    if (res.status === 202 && data.task_id) {
      startGlobalTask(data.task_id); // из global.js
      showToast('Задача запущена', 'info');
    } else {
      throw new Error(data.detail || 'Неизвестный ответ сервера');
    }
  } catch (err) {
    showToast(err.message, 'error');
    submitBtn.disabled = false;
  }
});

// Если задача уже идёт — блокируем кнопку
if (sessionStorage.getItem('invoice_task_id')) {
  submitBtn.disabled = true;
  submitBtn.textContent = 'Задача выполняется…';
}