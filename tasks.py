from abc import ABC, abstractmethod
import json
import os
from datetime import datetime

TASKS_FILE = 'tasks.json'


class BaseTask(ABC):
    """Абстрактный класс — шаблон для всех задач"""
    
    @abstractmethod
    def info(self):
        """Каждый наследник ОБЯЗАН реализовать этот метод"""
        pass
    
    @abstractmethod
    def to_dict(self):
        """Для сохранения в JSON"""
        pass


class Task(BaseTask):
    
    def __init__(self, text, priority="normal"):
        self.text = text        
        self._done = False     
        self.__priority = priority  
    

    @property
    def priority(self):
        return self.__priority
    
    @priority.setter
    def priority(self, value):
        allowed = ["low", "normal", "high"]
        if value in allowed:
            self.__priority = value
        else:
            print(f"Приоритет должен быть одним из: {allowed}")
    
    @property
    def done(self):
        return self._done
    
    def mark_done(self):
        self._done = True
    
    def info(self):
        """Полиморфизм — базовая реализация"""
        status = "✅" if self._done else "⬜"
        return f"{status} [{self.__priority.upper()}] {self.text}"
    
    def to_dict(self):
        return {
            "type": "task",
            "text": self.text,
            "done": self._done,
            "priority": self.__priority
        }
    
    def __str__(self):
        return self.info()


class UrgentTask(Task):
    
    def __init__(self, text, deadline):
        super().__init__(text, priority="high")
        self.deadline = deadline
    
    def info(self):
        """Полиморфизм — своя реализация"""
        status = "✅" if self.done else "🔥"
        return f"{status} [СРОЧНО до {self.deadline}] {self.text}"
    
    def to_dict(self):
        data = super().to_dict()
        data["type"] = "urgent"
        data["deadline"] = self.deadline
        return data


class TaskManager:
    
    def __init__(self):
        self.__tasks = []
        self.load()
    
    def load(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            for item in raw:
                if item.get("type") == "urgent":
                    t = UrgentTask(item["text"], item["deadline"])
                else:
                    t = Task(item["text"], item.get("priority", "normal"))
                if item.get("done"):
                    t.mark_done()
                self.__tasks.append(t)
    
    def save(self):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.__tasks], f,
                      ensure_ascii=False, indent=4)
    
    def add(self, text, urgent=False, deadline=None):
        if urgent and deadline:
            task = UrgentTask(text, deadline)
        else:
            task = Task(text)
        self.__tasks.append(task)
        self.save()
        return task
    
    def delete(self, index):
        if 0 <= index < len(self.__tasks):
            removed = self.__tasks.pop(index)
            self.save()
            return removed
        return None
    
    def mark_done(self, index):
        if 0 <= index < len(self.__tasks):
            self.__tasks[index].mark_done()
            self.save()
            return self.__tasks[index]
        return None
    
    def get_all(self):
        return self.__tasks
    
    def sort_by_priority(self):
        """Сортировка — тема из Lab 2!"""
        order = {"high": 0, "normal": 1, "low": 2}
        return sorted(self.__tasks,
                      key=lambda t: order.get(t.priority, 1))
    
    def search(self, keyword):
        """Поиск по ключевому слову"""
        return [t for t in self.__tasks
                if keyword.lower() in t.text.lower()]






def main():
    manager = TaskManager()
    print("Todo-бот v2.0 (ООП)")

    while True:
        print("\n1. Показать  2. Добавить  3. Удалить  4. Выполнено  5. Выйти")
        command = input("Команда: ").strip()

        if command == '1':
            tasks = manager.get_all()
            if not tasks:
                print("Задач нет!")
            for i, t in enumerate(tasks, 1):
                print(f"{i}. {t.info()}")

        elif command == '2':
            text = input("Описание задачи: ")
            urgent = input("Срочная? (да/нет): ").lower() == 'да'
            if urgent:
                deadline = input("Дедлайн (например 01-06-2025): ")
                manager.add(text, urgent=True, deadline=deadline)
            else:
                manager.add(text)
            print("Добавлено!")

        elif command == '3':
            for i, t in enumerate(manager.get_all(), 1):
                print(f"{i}. {t}")
            num = int(input("Номер для удаления: ")) - 1
            removed = manager.delete(num)
            if removed:
                print(f"Удалено: {removed.text}")

        elif command == '4':
            for i, t in enumerate(manager.get_all(), 1):
                print(f"{i}. {t}")
            num = int(input("Номер выполненной: ")) - 1
            manager.mark_done(num)
            print("Отмечено!")

        elif command == '5':
            break

if __name__ == "__main__":
    main()