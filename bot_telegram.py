import telebot
import django
import os
import sys
import re
import requests


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from bot.models import Task, UserQuery

BOT_TOKEN = 'TOKEN HERE'
bot = telebot.TeleBot(BOT_TOKEN)



def get_or_create_user(telegram_id, username):
    """Получаем или создаём пользователя в БД"""
    user, created = User.objects.get_or_create(
        username=f"tg_{telegram_id}",
        defaults={'first_name': username or 'Unknown'}
    )
    return user

def validate_date(date_str):
    """Регулярное выражение для проверки даты — тема Lab 3!"""
    pattern = r'^\d{2}-\d{2}-\d{4}$'
    return re.match(pattern, date_str) is not None

def get_weather(city="Almaty"):
    """Запрос к API погоды — тема Lab 4!"""
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return "Погода недоступна"
    except Exception:
        return "Ошибка при получении погоды"
    

def get_quote():
    """Парсинг мотивационной цитаты — тема Lab 5!"""
    try:
        import time
        from bs4 import BeautifulSoup
        url = 'https://quotes.toscrape.com'
        response = requests.get(url, timeout=5)
        time.sleep(1)  # вежливая пауза между запросами
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = soup.find_all('div', class_='quote')
        if quotes:
            import random
            quote = random.choice(quotes)
            text = quote.find('span', class_='text').text
            author = quote.find('small', class_='author').text
            return f'"{text}"\n\n— {author}'
        return "Цитата недоступна"
    except Exception as e:
        return "Ошибка при получении цитаты"


def sort_tasks(tasks):
    """Сортировка задач — тема Lab 2!"""
    order = {'high': 0, 'normal': 1, 'low': 2}
    return sorted(tasks, key=lambda t: order.get(t.priority, 1))

def main_keyboard():
    """Inline кнопки главного меню"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton("📋 Мои задачи", callback_data="show"),
        telebot.types.InlineKeyboardButton("➕ Добавить", callback_data="add")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("🗑 Удалить", callback_data="delete"),
        telebot.types.InlineKeyboardButton("✅ Выполнено", callback_data="done")
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton("🌤 Погода", callback_data="weather"),
        telebot.types.InlineKeyboardButton("💬 Цитата", callback_data="quote")
    )
    return keyboard



@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.first_name or "друг"
    get_or_create_user(message.from_user.id, username)
    

    UserQuery.objects.create(
        telegram_id=message.from_user.id,
        username=username,
        message='/start'
    )
    
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {username}!\n\nЯ твой Todo-бот. Выбери действие:",
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = """
📌 *Команды бота:*

/start — главное меню
/help — помощь
/add — добавить задачу
/list — список задач
/weather — погода в Алматы

Или используй кнопки меню!
    """
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['list'])
def list_tasks_cmd(message):
    list_tasks(message.chat.id, message.from_user.id, message.from_user.first_name)

def list_tasks(chat_id, user_id, first_name):
    user = get_or_create_user(user_id, first_name)
    tasks = Task.objects.filter(user=user)
    
    if not tasks:
        bot.send_message(chat_id, "У тебя пока нет задач! Добавь первую 👇",
                        reply_markup=main_keyboard())
        return
    
    sorted_tasks = sort_tasks(list(tasks))
    text = "📋 *Твои задачи:*\n\n"
    for i, task in enumerate(sorted_tasks, 1):
        status = "✅" if task.done else "⬜"
        priority_emoji = {"high": "🔥", "normal": "📌", "low": "💤"}.get(task.priority, "📌")
        deadline = f" (до {task.deadline})" if task.deadline else ""
        text += f"{i}. {status} {priority_emoji} {task.text}{deadline}\n"
    
    bot.send_message(chat_id, text, parse_mode='Markdown',
                    reply_markup=main_keyboard())

@bot.message_handler(commands=['weather'])
def weather_cmd(message):
    weather = get_weather("Almaty")
    bot.send_message(message.chat.id, f"🌤 *Погода:*\n{weather}", parse_mode='Markdown')



user_states = {} 

@bot.callback_query_handler(func=lambda call: not call.data.startswith('priority_'))
def handle_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    if call.data == "show":
        list_tasks(call.message.chat.id, call.from_user.id, call.from_user.first_name)
    
    elif call.data == "add":
        user_states[user_id] = 'waiting_task_text'
        bot.send_message(chat_id, "✏️ Напиши текст новой задачи:")
    
    elif call.data == "delete":
        user = get_or_create_user(user_id, call.from_user.first_name)
        tasks = list(Task.objects.filter(user=user, done=False))
        if not tasks:
            bot.send_message(chat_id, "Нет задач для удаления!")
            return
        text = "Выбери номер задачи для удаления:\n\n"
        for i, task in enumerate(tasks, 1):
            text += f"{i}. {task.text}\n"
        user_states[user_id] = ('waiting_delete', tasks)
        bot.send_message(chat_id, text)
    
    elif call.data == "done":
        user = get_or_create_user(user_id, call.from_user.first_name)
        tasks = list(Task.objects.filter(user=user, done=False))
        if not tasks:
            bot.send_message(chat_id, "Нет активных задач!")
            return
        text = "Выбери номер выполненной задачи:\n\n"
        for i, task in enumerate(tasks, 1):
            text += f"{i}. {task.text}\n"
        user_states[user_id] = ('waiting_done', tasks)
        bot.send_message(chat_id, text)
    
    elif call.data == "weather":
        weather = get_weather("Almaty")
        bot.send_message(chat_id, f"🌤 Погода в Алматы:\n{weather}")

    elif call.data == "quote":
        quote = get_quote()
        bot.send_message(chat_id, f"💬 *Мотивация дня:*\n\n{quote}", parse_mode='Markdown')
    
    bot.answer_callback_query(call.id)



@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    state = user_states.get(user_id)
    
    if state == 'waiting_task_text':
        user_states[user_id] = ('waiting_priority', message.text)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("🔥 Высокий", callback_data="priority_high"),
            telebot.types.InlineKeyboardButton("📌 Обычный", callback_data="priority_normal"),
            telebot.types.InlineKeyboardButton("💤 Низкий", callback_data="priority_low")
        )
        bot.send_message(chat_id, "Выбери приоритет задачи:", reply_markup=keyboard)
    
    elif isinstance(state, tuple) and state[0] == 'waiting_delete':
        tasks = state[1]
        try:
            num = int(message.text) - 1
            if 0 <= num < len(tasks):
                task_text = tasks[num].text
                tasks[num].delete()
                user_states.pop(user_id, None)
                bot.send_message(chat_id, f"🗑 Задача '{task_text}' удалена!",
                                reply_markup=main_keyboard())
            else:
                bot.send_message(chat_id, "Неверный номер, попробуй ещё раз.")
        except ValueError:
            bot.send_message(chat_id, "Введи число!")
    
    elif isinstance(state, tuple) and state[0] == 'waiting_done':
        tasks = state[1]
        try:
            num = int(message.text) - 1
            if 0 <= num < len(tasks):
                tasks[num].done = True
                tasks[num].save()
                user_states.pop(user_id, None)
                bot.send_message(chat_id, f"✅ Задача '{tasks[num].text}' выполнена!",
                                reply_markup=main_keyboard())
            else:
                bot.send_message(chat_id, "Неверный номер, попробуй ещё раз.")
        except ValueError:
            bot.send_message(chat_id, "Введи число!")
    
    else:
        bot.send_message(chat_id, "Используй меню 👇", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('priority_'))
def handle_priority(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    state = user_states.get(user_id)
    
    priority = call.data.replace('priority_', '')
    

    if isinstance(state, tuple) and state[0] == 'waiting_priority':
        task_text = state[1]
    elif isinstance(state, str):
        task_text = state
    else:
        bot.send_message(chat_id, "Что-то пошло не так, попробуй ещё раз.")
        bot.answer_callback_query(call.id)
        return
    
    user = get_or_create_user(user_id, call.from_user.first_name)
    
    Task.objects.create(
        user=user,
        text=task_text,
        priority=priority
    )
    
    UserQuery.objects.create(
        telegram_id=user_id,
        username=call.from_user.first_name,
        message=f'add_task: {task_text}'
    )
    
    user_states.pop(user_id, None)
    bot.send_message(chat_id, f"✅ Задача добавлена!\n📌 {task_text}",
                    reply_markup=main_keyboard())
    bot.answer_callback_query(call.id)



print("🤖 Бот запущен!")
bot.polling(none_stop=True)