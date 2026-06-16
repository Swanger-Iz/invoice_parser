// Получаем элементы
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const submitBtn = document.getElementById('submitBtn');
const resultsArea = document.getElementById('resultsArea');
const errorArea = document.getElementById('errorArea');
const errorMessage = document.getElementById('errorMessage');
const constructorName = document.getElementById('constructorName');
const customerName = document.getElementById('customerName');
const statusBadge = document.getElementById('statusBadge');
const clearResults = document.getElementById('clearResults');
const downloadResult = document.getElementById('downloadResult');
const timestamp = document.getElementById('timestamp');

let selectedFile = null;
let currentResult = null;

// Обновляем время
function updateTimestamp() {
    timestamp.textContent = new Date().toLocaleTimeString();
}
updateTimestamp();
setInterval(updateTimestamp, 10000);

// Клик для выбора файла
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Выбор файла через input
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Обработка файла
function handleFile(file) {
    // Проверяем тип
    if (!file.type.startsWith('image/')) {
        showError('Пожалуйста, выберите изображение');
        return;
    }
    
    // Проверяем размер (20 МБ = 20 * 1024 * 1024 байт)
    const maxSize = 20 * 1024 * 1024;
    if (file.size > maxSize) {
        showError(`Файл слишком большой (${(file.size / 1024 / 1024).toFixed(1)} МБ). Максимум 20 МБ`);
        return;
    }
    
    selectedFile = file;
    
    // Показываем информацию о файле
    fileName.textContent = file.name;
    fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} МБ`;
    fileInfo.style.display = 'flex';
    uploadArea.classList.add('has-file');
    submitBtn.disabled = false;
    errorArea.style.display = 'none';
    
    // Показываем превью
    previewImage(file);
    
    // Скрываем предыдущие результаты
    resultsArea.style.display = 'none';
}

// Предпросмотр изображения
function previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        // Удаляем старый превью если есть
        const oldPreview = uploadArea.querySelector('.preview-image');
        if (oldPreview) oldPreview.remove();
        
        const img = document.createElement('img');
        img.src = e.target.result;
        img.className = 'preview-image';
        uploadArea.appendChild(img);
    };
    reader.readAsDataURL(file);
}

// Удаление файла
removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

function clearFile() {
    selectedFile = null;
    fileInfo.style.display = 'none';
    uploadArea.classList.remove('has-file');
    submitBtn.disabled = true;
    fileInput.value = '';
    resultsArea.style.display = 'none';
    errorArea.style.display = 'none';
    
    // Удаляем превью
    const preview = uploadArea.querySelector('.preview-image');
    if (preview) preview.remove();
}

// Отправка файла
submitBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    // Подготовка к отправке
    const formData = new FormData();
    formData.append('upload_file', selectedFile);
    
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = '<span>⏳</span> Обработка...';
    
    try {
        const response = await fetch('/images', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }
        
        const data = await response.json();
        currentResult = data;
        
        // Обрабатываем ответ
        handleResponse(data);
        
    } catch (error) {
        showError(`Ошибка соединения: ${error.message}`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<span>🔍</span> Распознать';
    }
});

// Обработка ответа от сервера
function handleResponse(data) {
    resultsArea.style.display = 'block';
    errorArea.style.display = 'none';
    
    // Статус
    const status = data.Status;
    statusBadge.textContent = status;
    statusBadge.className = 'status-badge';
    
    if (status === 'OK') {
        statusBadge.classList.add('success');
        constructorName.textContent = data.Constructor_name || '—';
        customerName.textContent = data.Customer_name || '—';
        constructorName.classList.remove('empty');
        customerName.classList.remove('empty');
        
        // Анимация
        document.querySelectorAll('.result-item').forEach((item, index) => {
            item.style.animation = `slideUp 0.5s ease ${index * 0.1}s both`;
        });
        
    } else if (status === 'NO_FOUND') {
        statusBadge.classList.add('warning');
        constructorName.textContent = 'Не найдено';
        customerName.textContent = 'Не найдено';
        constructorName.classList.add('empty');
        customerName.classList.add('empty');
        
    } else if (status === 'FILE_IS_TOO_BIG') {
        statusBadge.classList.add('error');
        showError('Файл слишком большой (максимум 20 МБ)');
        resultsArea.style.display = 'none';
        return;
    } else {
        statusBadge.classList.add('error');
        constructorName.textContent = 'Ошибка';
        customerName.textContent = 'Ошибка';
        constructorName.classList.add('empty');
        customerName.classList.add('empty');
    }
}

// Показ ошибки
function showError(message) {
    errorMessage.textContent = message;
    errorArea.style.display = 'flex';
    resultsArea.style.display = 'none';
    
    // Автоскрытие через 5 секунд
    clearTimeout(window.errorTimeout);
    window.errorTimeout = setTimeout(() => {
        errorArea.style.display = 'none';
    }, 5000);
}

// Очистка результатов
clearResults.addEventListener('click', () => {
    resultsArea.style.display = 'none';
    currentResult = null;
    constructorName.textContent = '—';
    customerName.textContent = '—';
    constructorName.classList.remove('empty');
    customerName.classList.remove('empty');
    clearFile();
});

// Скачивание результата
downloadResult.addEventListener('click', () => {
    if (!currentResult) return;
    
    const data = {
        timestamp: new Date().toISOString(),
        result: currentResult
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `result_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Обработка ошибок глобально
window.addEventListener('unhandledrejection', (event) => {
    showError(`Необработанная ошибка: ${event.reason}`);
});