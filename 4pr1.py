import json
import os
import threading
import time
from datetime import datetime, timedelta

class Logger:
    def __init__(self, username):
        self.username = username
        self.log_file = f"logs_{username}.log"

    def log_info(self, action):
        with open(self.log_file, "a") as file:
            file.write(f"[INFO] [{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [{self.username}] – {action}\n")

    def log_error(self, error_message):
        with open(self.log_file, "a") as file:
            file.write(f"[ERROR] [{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] [{self.username}] – {error_message}\n")

class UserManager:
    def __init__(self, logger):
        self.users_file = "users.json"
        self.logger = logger
        self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as file:
                self.users = json.load(file)
        else:
            self.users = {}

    def save_users(self):
        with open(self.users_file, "w") as file:
            json.dump(self.users, file)

    def register(self, username, password):
        if username in self.users:
            print("Пользователь уже существует.")
            return False
        self.users[username] = {"password": password}
        self.save_users()
        self.logger.log_info(f"Пользователь {username} зарегистрирован.")
        print("Регистрация успешна.")
        return True

    def login(self, username, password):
        if username in self.users and self.users[username]["password"] == password:
            self.logger.log_info(f"Пользователь {username} вошел в систему.")
            print("Вход выполнен успешно.")
            return True
        print("Неверный логин или пароль.")
        return False

class NoteManager:
    def __init__(self, username, logger):
        self.username = username
        self.notes_file = f"notes_{username}.json"
        self.notes = []
        self.lock = threading.Lock()
        self.logger = logger
        self.load_notes()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r") as file:
                self.notes = json.load(file)

    def save_notes(self):
        with self.lock:
            with open(self.notes_file, "w") as file:
                json.dump(self.notes, file)

    def add_note(self, title, content):
            with self.lock:
                for note in self.notes:
                    if note["title"] == title:
                        print("Заметка с таким заголовком уже существует. Введите другой заголовок.")
                        return
                self.notes.append({"title": title, "content": content})
                self.logger.log_info(f"Добавлена заметка: {title}")
                print("Заметка добавлена.")

    def remove_note(self, title):
        with self.lock:
            self.notes = [note for note in self.notes if note["title"] != title]
            self.logger.log_info(f"Удалена заметка: {title}")
            print("Заметка удалена.")

    def edit_note(self, title, new_content):
        with self.lock:
            for note in self.notes:
                if note["title"] == title:
                    note["content"] = new_content
                    self.logger.log_info(f"Изменена заметка: {title}")
                    print("Заметка изменена.")
                    return
            print("Заметка не найдена.")

    def show_notes(self):
        if not self.notes:
            print("Заметок нет.")
        else:
            for note in self.notes:
                print(f"{note['title']}: {note['content']}")

def auto_save(manager):
    while True:
        time.sleep(5)
        manager.save_notes()

def license_checker(start_time, license_duration, logger):
    while True:
        if datetime.now() > start_time + timedelta(minutes=license_duration):
            logger.log_info("Пробная лицензия программы завершена.")
            print("Пробная лицензия программы завершена, чтобы продолжить работу приобретите лицензионный ключ!")
            os._exit(0)  # Завершение программы
        time.sleep(60)  # Проверка каждую минуту

def main():
    logger = Logger("system")
    user_manager = UserManager(logger)
    username = input("Введите логин: ")
    password = input("Введите пароль: ")

    if not user_manager.login(username, password):
        choice = input("Хотите зарегистрироваться? (да/нет): ")
        if choice.lower() == "да":
            username = input("Введите новый логин: ")
            password = input("Введите новый пароль: ")
            user_manager.register(username, password)
        else:
            return

    logger = Logger(username)
    note_manager = NoteManager(username, logger)

    save_thread = threading.Thread(target=auto_save, args=(note_manager,))
    save_thread.daemon = True
    save_thread.start()

    license_duration = 30  # 30 минут пробной лицензии
    license_thread = threading.Thread(target=license_checker, args=(datetime.now(), license_duration, logger))
    license_thread.daemon = True
    license_thread.start()

    while True:
        print("\n1. Показать заметки")
        print("2. Добавить заметку")
        print("3. Удалить заметку")
        print("4. Редактировать заметку")
        print("5. Выйти")
        choice = input("Выберите действие: ")

        try:
            if choice == "1":
                note_manager.show_notes()
            elif choice == "2":
                title = input("Введите заголовок: ")
                content = input("Введите содержание: ")
                note_manager.add_note(title, content)
            elif choice == "3":
                title = input("Введите заголовок для удаления: ")
                note_manager.remove_note(title)
            elif choice == "4":
                title = input("Введите заголовок для редактирования: ")
                new_content = input("Введите новое содержание: ")
                note_manager.edit_note(title, new_content)
            elif choice == "5":
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите действие от 1 до 5.")
                logger.log_error(f"Неверный выбор действия: {choice}")
        except Exception as e:
            logger.log_error(f"Ошибка: {str(e)}")
            print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()