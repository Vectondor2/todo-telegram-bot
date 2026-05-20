# 📝 Todo Telegram Bot

## Описание проекта
Telegram чат-бот для управления личными задачами. 
Позволяет добавлять, удалять и просматривать задачи прямо в Telegram.

## Используемые технологии
- Python 3
- pyTelegramBotAPI — Telegram бот
- Django — база данных и админка
- SQLite — хранение данных
- BeautifulSoup — парсинг цитат
- requests — запросы к API

## Функции бота
- /start — главное меню
- /help — список команд
- /list — просмотр задач
- /weather — погода в Алматы
- /quote — мотивационная цитата
- Добавление, удаление, отметка задач через кнопки

## Установка

1. Клонируй репозиторий
2. Установи зависимости:
pip install -r requirements.txt

3. Примени миграции:
python manage.py migrate

4. Запусти бота:
python bot_telegram.py

## Структура проекта
- bot_telegram.py — основной файл бота
- tasks.py — ООП архитектура
- todo_bot.py — консольная версия
- bot/models.py — модели базы данных
- config/settings.py — настройки Django

## Автор
Серікұлы Нұрдәулет
