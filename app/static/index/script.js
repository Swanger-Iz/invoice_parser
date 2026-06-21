// Скрипты только для главной страницы
console.log('Главная страница загружена');

// Обновление времени (если нужно дополнительное поведение)
document.addEventListener('DOMContentLoaded', function() {
    const timestamp = document.getElementById('timestamp');
    if (timestamp) {
        timestamp.textContent = new Date().toLocaleTimeString();
    }
});