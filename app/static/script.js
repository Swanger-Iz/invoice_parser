// ===== ГЛОБАЛЬНЫЕ УТИЛИТЫ =====

// Обновление времени в футере на всех страницах
function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    if (timestamp) {
        timestamp.textContent = new Date().toLocaleTimeString();
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Обновляем время сразу
    updateTimestamp();
    
    // И каждые 10 секунд
    setInterval(updateTimestamp, 10000);
    
    // Обработка кликов по хлебным крошкам (навигация)
    document.querySelectorAll('.breadcrumb-item:not(.active)').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href) {
                window.location.href = href;
            }
        });
    });
});

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

// Форматирование размера файла
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Б';
    const k = 1024;
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Валидация изображения
function isValidImage(file) {
    return file.type.startsWith('image/');
}

// Получить расширение файла
function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

// ===== ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК =====
window.addEventListener('unhandledrejection', (event) => {
    console.error('Необработанная ошибка:', event.reason);
});

// ===== КОНСОЛЬНЫЙ ДЕБАГ =====
console.log('✅ Глобальные скрипты загружены');