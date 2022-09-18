import datetime
import json
import os.path
import requests
from sys import platform


# Запись файла
def write_file_with_template(path, temp):
    f = open(path, 'w+')
    f.write(temp)
    f.close()


# Ссылки для API
todos = 'https://json.medrocket.ru/todos'
users = 'https://json.medrocket.ru/users'
# Словари для todos и users
# Проверка на подключение к сайту
while True:
    if requests.get('https://json.medrocket.ru').status_code:
        response_todos = requests.get(todos)
        todos = json.loads(response_todos.text)
        response_users = requests.get(users)
        users = json.loads(response_users.text)
        break
    else:
        print('Нет подключения к https://json.medrocket.ru')
# Подсчёт общих задач
true_todos_by_user = {}  # Выполненные задачи
false_todos_by_users = {}  # Невыполненные задачи
for todo in todos:
    if todo.get('completed'):
        try:
            true_todos_by_user[todo.get('userId')] += 1
        except KeyError:
            true_todos_by_user[todo.get('userId')] = 1
    else:
        try:
            false_todos_by_users[todo.get('userId')] += 1
        except KeyError:
            false_todos_by_users[todo.get('userId')] = 1
# Дата отчёта
today = datetime.datetime.today()
# Создание папки tasks
if not os.path.isdir('./tasks'):
    os.mkdir('./tasks')
# Выборка задач для отчёта и запись в файл
for user in users:
    # Выборка задач для отчёта
    true_todos = ''
    false_todos = ''
    for todo in todos:
        title = todo.get('title')
        if todo.get('completed') and title is not None and user.get("id") == todo.get('userId'):
            if len(title) > 48:
                true_todos += f'\n{title[:48]}...'
            else:
                true_todos += f'\n{title}'
        elif todo.get('title') is not None and user.get("id") == todo.get('userId'):
            if len(title) > 48:
                false_todos += f'\n{title[:48]}...'
            else:
                false_todos += f'\n{title}'
    # Шаблон для записи
    template = f'Отчёт для {user.get("company").get("name")}.\n{user.get("name")} <{user.get("email")}> ' \
               f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
               f'{true_todos_by_user[user.get("id")] + false_todos_by_users[user.get("id")]}\n\nЗавершённые задачи (' \
               f'{true_todos_by_user[user.get("id")]}):{true_todos}\n\nОставшиеся задачи (' \
               f'{false_todos_by_users[user.get("id")]}):{false_todos}'
    # Пути до файлов
    path_to_file = f'./tasks/{user.get("username")}.txt'
    path_to_old_file_for_linux = f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}T' \
                                 f'{today.strftime("%H:%M")}.txt'
    path_to_old_file_for_windows = f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}' \
                                   f'T{today.strftime("%H.%M")}.txt'
    # Запись в файл
    if os.path.isfile(path_to_file):
        # Проверка системы, где работает скрипт
        if platform == "linux" or platform == "linux2":
            # Проверка на то, есть ли старый отчёт (возможно использование скрипта в ту же минуту)
            if os.path.isfile(path_to_old_file_for_linux):
                os.rename(path_to_file, f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}T'
                                        f'{today.strftime("%H:%M:%S")}.txt')
                write_file_with_template(path_to_file, template)
            else:
                os.rename(path_to_file, path_to_old_file_for_linux)
                write_file_with_template(path_to_file, template)
        else:
            # Проверка на то, есть ли старый отчёт (возможно использование скрипта в ту же минуту)
            if os.path.isfile(path_to_old_file_for_windows):
                os.rename(path_to_file, f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}T'
                                        f'{today.strftime("%H.%M.%S")}.txt')
                write_file_with_template(path_to_file, template)
            else:
                os.rename(path_to_file, path_to_old_file_for_windows)
                write_file_with_template(path_to_file, template)
    else:
        write_file_with_template(path_to_file, template)
