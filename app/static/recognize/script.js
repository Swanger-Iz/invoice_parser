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
const processingTime = document.getElementById('processingTime');
const elapsedTime = document.getElementById('elapsedTime');
const resultTime = document.getElementById('resultTime');
const finalTime = document.getElementById('finalTime');

const MAX_SIZE_MB = 20;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

let selectedFile = null;
let currentResult = null;
let startTime = null;
let timerInterval = null;

// Обновляем время
function updateTimestamp() {
    if (timestamp) {
        timestamp.textContent = new Date().toLocaleTimeString();
    }
}
updateTimestamp();
setInterval(updateTimestamp, 10000);

// Клик для выбора файла
if (uploadArea) {
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
}

// Drag and Drop
if (uploadArea) {
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
}

// Выбор файла через input
if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
}

// Обработка файла
function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Пожалуйста, выберите изображение');
        return;
    }
    
    selectedFile = file;
    const sizeMB = file.size / 1024 / 1024;
    
    fileName.textContent = file.name;
    fileSize.textContent = `${sizeMB.toFixed(2)} МБ`;
    fileInfo.style.display = 'flex';
    if (uploadArea) uploadArea.classList.add('has-file');
    errorArea.style.display = 'none';
    
    if (file.size > MAX_SIZE_BYTES) {
        fileSize.className = 'file-size over-limit';
        submitBtn.disabled = true;
        showError(`Файл слишком большой (${sizeMB.toFixed(1)} МБ). Максимум ${MAX_SIZE_MB} МБ`);
        const preview = uploadArea ? uploadArea.querySelector('.preview-image') : null;
        if (preview) preview.remove();
        return;
    } else {
        fileSize.className = 'file-size under-limit';
        submitBtn.disabled = false;
        errorArea.style.display = 'none';
        previewImage(file);
    }
    
    resultsArea.style.display = 'none';
    processingTime.classList.remove('active');
    resultTime.style.display = 'none';
    stopTimer();
}

// Предпросмотр изображения
function previewImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        if (!uploadArea) return;
        const oldPreview = uploadArea.querySelector('.preview-image');
        if (oldPreview) oldPreview.remove();
        
        const img = document.createElement('img');
        img.src = e.target.result;
        img.className = 'preview-image';
        img.alt = 'Предпросмотр';
        uploadArea.appendChild(img);
    };
    reader.readAsDataURL(file);
}

// Удаление файла
if (removeFile) {
    removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });
}

function clearFile() {
    selectedFile = null;
    fileInfo.style.display = 'none';
    if (uploadArea) uploadArea.classList.remove('has-file');
    submitBtn.disabled = true;
    if (fileInput) fileInput.value = '';
    resultsArea.style.display = 'none';
    errorArea.style.display = 'none';
    currentResult = null;
    processingTime.classList.remove('active');
    resultTime.style.display = 'none';
    stopTimer();
    
    if (uploadArea) {
        const preview = uploadArea.querySelector('.preview-image');
        if (preview) preview.remove();
    }
    
    fileSize.className = 'file-size under-limit';
}

// Запуск таймера
function startTimer() {
    startTime = Date.now();
    processingTime.classList.add('active');
    elapsedTime.textContent = '0.0';
    
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        elapsedTime.textContent = elapsed.toFixed(1);
    }, 100);
}

// Остановка таймера
function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    processingTime.classList.remove('active');
}

// Отправка файла
if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        
        if (selectedFile.size > MAX_SIZE_BYTES) {
            showError(`Файл слишком большой (${(selectedFile.size / 1024 / 1024).toFixed(1)} МБ). Максимум ${MAX_SIZE_MB} МБ`);
            submitBtn.disabled = true;
            return;
        }
        
        const formData = new FormData();
        formData.append('upload_file', selectedFile);
        
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = '<span>⏳</span> Обработка...';
        errorArea.style.display = 'none';
        resultsArea.style.display = 'none';
        resultTime.style.display = 'none';
        
        startTimer();
        
        try {
            const response = await fetch('/api/get_fio', {
                method: 'POST',
                body: formData
            });
            
            stopTimer();
            const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
            
            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }
            
            const data = await response.json();
            currentResult = data;
            
            finalTime.textContent = totalTime;
            resultTime.style.display = 'block';
            
            handleResponse(data);
            
        } catch (error) {
            stopTimer();
            showError(`Ошибка соединения: ${error.message}`);
            resultTime.style.display = 'none';
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            submitBtn.innerHTML = '<span>🔍</span> Распознать';
        }
    });
}

// Обработка ответа от сервера
function handleResponse(data) {
    resultsArea.style.display = 'block';
    errorArea.style.display = 'none';
    
    const status = String(data.Status).toUpperCase().trim();
    statusBadge.textContent = data.Status;
    statusBadge.className = 'status-badge';
    
    if (status === 'SUCCESS' || status === 'GOOD') {
        statusBadge.classList.add('success');
        constructorName.textContent = data.Constructor_name || '—';
        customerName.textContent = data.Customer_name || '—';
        constructorName.classList.remove('empty');
        customerName.classList.remove('empty');
        
    } else if (status === 'BAD' || status === 'NOT_FOUND' || status === 'NO_FOUND') {
        statusBadge.classList.add('warning');
        constructorName.textContent = 'Не найдено';
        customerName.textContent = 'Не найдено';
        constructorName.classList.add('empty');
        customerName.classList.add('empty');
        
    } else if (status === 'FILE_IS_TOO_BIG') {
        statusBadge.classList.add('error');
        showError(`Файл слишком большой (максимум ${MAX_SIZE_MB} МБ)`);
        resultsArea.style.display = 'none';
        resultTime.style.display = 'none';
        submitBtn.disabled = true;
        return;
        
    } else if (status === 'WRONG_FILE_FORMAT') {
        statusBadge.classList.add('error');
        showError('Неподдерживаемый формат файла. Используйте JPG или PNG');
        resultsArea.style.display = 'none';
        resultTime.style.display = 'none';
        return;
        
    } else if (status === 'ERROR') {
        statusBadge.classList.add('error');
        constructorName.textContent = 'Ошибка сервера';
        customerName.textContent = 'Ошибка сервера';
        constructorName.classList.add('empty');
        customerName.classList.add('empty');
        
    } else {
        statusBadge.classList.add('error');
        constructorName.textContent = `Неизвестный статус: ${data.Status}`;
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
    resultTime.style.display = 'none';
    
    clearTimeout(window.errorTimeout);
    window.errorTimeout = setTimeout(() => {
        errorArea.style.display = 'none';
    }, 5000);
}

// Очистка результатов
if (clearResults) {
    clearResults.addEventListener('click', () => {
        resultsArea.style.display = 'none';
        currentResult = null;
        constructorName.textContent = '—';
        customerName.textContent = '—';
        constructorName.classList.remove('empty');
        customerName.classList.remove('empty');
        resultTime.style.display = 'none';
        clearFile();
    });
}

// Скачивание результата
if (downloadResult) {
    downloadResult.addEventListener('click', () => {
        if (!currentResult) return;
        
        const data = {
            timestamp: new Date().toISOString(),
            processing_time: finalTime.textContent,
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
}