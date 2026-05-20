
import json
import os

TASKS_FILE = 'tasks.json'



def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        return tasks
    else:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)


def show_tasks(tasks):
    if not tasks:
        print("У тебя пока нет задач. Празднуй!")
    else:
        print("\n Твои задачи:")
        for index, task in enumerate(tasks):
            status = "✅" if task['done'] else "⬜"
            print(f"{index + 1}. {status} {task['text']}")

def add_task(tasks):

    task_text = input("Введи описание новой задачи: ")
    new_task = {"text": task_text, "done": False}
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Задача '{task_text}' добавлена!")

def delete_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return

    try:
        task_num = int(input("Введи номер задачи для удаления: "))
        index_to_delete = task_num - 1

        if 0 <= index_to_delete < len(tasks):
            removed_task = tasks.pop(index_to_delete)
            save_tasks(tasks)
            print(f"Задача '{removed_task['text']}' удалена.")
        else:
            print("Задачи с таким номером нет.")

    except ValueError:
        print("Пожалуйста, введи число.")

def mark_done(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    try:
        task_num = int(input("Введи номер выполненной задачи: "))
        index_to_mark = task_num - 1
        if 0 <= index_to_mark < len(tasks):
            tasks[index_to_mark]['done'] = True
            save_tasks(tasks)
            print(f"⭐ Отлично! Задача '{tasks[index_to_mark]['text']}' выполнена.")
        else:
            print("Задачи с таким номером нет.")
    except ValueError:
        print("Пожалуйста, введи число.")

def main():
    tasks = load_tasks()
    print("Добро пожаловать в Todo-бот v1.0 (Консольный)")


    while True:
        print("\n--- Что делаем? ---")
        print("1. Показать задачи (show)")
        print("2. Добавить задачу (add)")
        print("3. Удалить задачу (del)")
        print("4. Отметить задачу выполненной (done)")
        print("5. Выйти (exit)")

        command = input("Введи команду: ").lower().strip()

        if command == '1' or command == 'show':
            show_tasks(tasks)
        elif command == '2' or command == 'add':
            add_task(tasks)
        elif command == '3' or command == 'del':
            delete_task(tasks)
        elif command == '4' or command == 'done':
            mark_done(tasks)
        elif command == '5' or command == 'exit':
            print("Пока! Задачи сохранены в файл.")
            break
        else:
            print("Неизвестная команда. Попробуй еще раз.")

if __name__ == "__main__":
    main()
