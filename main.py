import datetime
import json
import os.path
import re
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
# Шаблон для регулярного выражения
regex = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=^_`{|}~-]+)*
|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]
|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])
|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]
|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
# Выборка задач для отчёта и запись в файл
for user in users:
    # Указана ли компания
    if user.get('company') is None:
        print(f'У пользователя {user.get("username")} не указана компания.')
        break
    # Указан ли email
    if user.get('email') is None:
        print(f'У пользователя {user.get("username")} не указана почта.')
        break
    # Валидация почты
    elif re.fullmatch(regex, user.get('email')):
        print(f'У пользователя {user.get("username")} неправильно указана почта.')
        break
    # Выборка задач для отчёта
    true_todos = ''
    false_todos = ''
    for todo in todos:
        title = todo.get('title')
        # Проверка на существование завершенных задач
        if todo.get('completed') and title is not None and user.get("id") == todo.get('userId'):
            if len(title) > 48:
                true_todos += f'\n{title[:48]}...'
            else:
                true_todos += f'\n{title}'
        # Проверка на существование оставшихся задач
        elif todo.get('title') is not None and user.get("id") == todo.get('userId'):
            if len(title) > 48:
                false_todos += f'\n{title[:48]}...'
            else:
                false_todos += f'\n{title}'
    # Шаблон для записи
    template = ''
    # Если у пользователя нет задач, то код начинает обрабатывать следующего
    if true_todos is None and false_todos is None:
        print(f'У пользователя {user.get("username")} нет задач.')
        break
    # Если у пользователя нет выполненных задач
    elif true_todos is None:
        template = f'Отчёт для {user.get("company").get("name")}.\n{user.get("name")} <{user.get("email")}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{true_todos_by_user[user.get("id")] + false_todos_by_users[user.get("id")]}\n' \
                   f'\nУ пользователя нет завершенных задач.\n\nОставшиеся задачи (' \
                   f'{false_todos_by_users[user.get("id")]}):{false_todos}'
    # Если у пользователя нет оставшихся задач
    elif false_todos is None:
        template = f'Отчёт для {user.get("company").get("name")}.\n{user.get("name")} <{user.get("email")}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{true_todos_by_user[user.get("id")] + false_todos_by_users[user.get("id")]}\n' \
                   f'\nЗавершённые задачи ({true_todos_by_user[user.get("id")]}):{true_todos}\n' \
                   f'\nУ пользователя нет оставшихся задач.'
    # У пользователя все есть.
    else:
        template = f'Отчёт для {user.get("company").get("name")}.\n{user.get("name")} <{user.get("email")}> ' \
               f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
               f'{true_todos_by_user[user.get("id")] + false_todos_by_users[user.get("id")]}\n' \
               f'\nЗавершённые задачи ({true_todos_by_user[user.get("id")]}):{true_todos}\n\nОставшиеся задачи (' \
               f'{false_todos_by_users[user.get("id")]}):{false_todos}'
    # Пути до файлов
    path_to_file = f'./tasks/{user.get("username")}.txt'
    path_to_old_file_for_linux = f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}T' \
                                 f'{today.strftime("%H:%M")}.txt'
    path_to_old_file_for_windows = f'./tasks/old_{user.get("username")}_{today.strftime("%Y-%m-%d")}' \
                                   f'T{today.strftime("%H.%M")}.txt'
    # Запись в файл
    if os.path.isfile(path_to_file):
        # Проверка операционной системы, где работает скрипт
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
