import datetime
import os.path
import re
import requests
from sys import platform


# Класс для записи пользователей
class User(object):
    def __init__(self, _id, name, username, email, company_name):
        self.id = _id
        self.name = name
        self.username = username
        self.email = email
        self.company_name = company_name


# Класс для записи задач
class Todo(object):
    def __init__(self, user_id, id, title, completed):
        self.user_id = user_id
        self.id = id
        self.title = title
        self.completed = completed


# Класс для проверки валидации
class Validator:
    # Шаблон для регулярного выражения
    regex = re.compile("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+"
                       ")*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|"
                       "\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*"
                       "[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?"
                       "[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:"
                       "(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|"
                       "\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])")

    # Валидация почты
    @staticmethod
    def is_valid_email(_email):
        return re.search(Validator.regex, _email)


# Класс для соединения с сайтом
class Connector:
    # Получение отклика от сайта
    @staticmethod
    def connection(path):
        if requests.get(path).status_code == 200:
            response = requests.get(path)
            return response.json()
        else:
            print('Нет соединения с интернетом или с сайтом')
            return Connector.connection(path)


# Загрузчик json в нужный класс
class JsonLoaderInClass:

    # Загрузка из json в User
    @staticmethod
    def loader_to_User(response):
        # Проверка валидности почты
        if Validator.is_valid_email(response.get('email')):
            return User(
                response.get('id'),
                response.get('name'),
                response.get('username'),
                response.get('email'),
                response.get('company').get('name')
            )
        else:
            return Exception

    # Загрузка из json в Td
    @staticmethod
    def loader_to_Todo(response):
        title = ''
        # Обрезка строки до 48 символов
        if len(response.get('title')) > 48:
            title = f'{response.get("title")[:48]}...'
        else:
            title = response.get('title')
        return Todo(
            response.get('userId'),
            response.get('id'),
            title,
            response.get('completed')
        )


# Создание папки tasks
if not os.path.isdir('./tasks'):
    os.mkdir('./tasks')
# Дата отчёта
today = datetime.datetime.today()


# Запись файла
def write_file_with_template(username, temp):
    path = f'./tasks/{username}.txt'
    path_to_old_file_for_linux = f'./tasks/old_{username}_{today.strftime("%Y-%m-%d")}T' \
                                 f'{today.strftime("%H:%M")}.txt'
    path_to_old_file_for_windows = f'./tasks/old_{username}_{today.strftime("%Y-%m-%d")}' \
                                   f'T{today.strftime("%H.%M")}.txt'
    # Существует ли файл
    if os.path.isfile(path):
        # Проверка операционной системы, где работает скрипт
        if platform == "linux" or platform == "linux2":
            # Проверка на то, есть ли старый отчёт (возможно использование скрипта в ту же минуту)
            if os.path.isfile(path_to_old_file_for_linux):
                os.rename(path, f'./tasks/old_{username}_{today.strftime("%Y-%m-%d")}T'
                                f'{today.strftime("%H:%M:%S")}.txt')
                f = open(path, 'w+')
                f.write(temp)
                f.close()
            else:
                os.rename(path, path_to_old_file_for_linux)
                f = open(path, 'w+')
                f.write(temp)
                f.close()
            pass
        else:
            # Проверка на то, есть ли старый отчёт (возможно использование скрипта в ту же минуту)
            if os.path.isfile(path_to_old_file_for_windows):
                os.rename(path, f'./tasks/old_{username}_{today.strftime("%Y-%m-%d")}T'
                                f'{today.strftime("%H.%M.%S")}.txt')
                f = open(path, 'w+')
                f.write(temp)
                f.close()
            else:
                os.rename(path, path_to_old_file_for_windows)
                f = open(path, 'w+')
                f.write(temp)
                f.close()
            pass
    else:
        f = open(path, 'w+')
        f.write(temp)
        f.close()


# Ссылки для получения json
todos = 'https://json.medrocket.ru/todos'
users = 'https://json.medrocket.ru/users'
# Подключение к сайту и загрузка json
response_users = Connector.connection(users)
response_todos = Connector.connection(todos)
# Словарь для users и todos и списки для хранения данных
users_match_with_todos = {}
urs = []
# Соотнесение пользователя и его задач
for user in response_users:
    urs.append(JsonLoaderInClass.loader_to_User(user))
    td = []
    for todo in response_todos:
        if todo.get('userId') == user.get('id'):
            td.append(JsonLoaderInClass.loader_to_Todo(todo))
    users_match_with_todos[f'{JsonLoaderInClass.loader_to_User(user).id}'] = td
# Запись отчётов
for u in urs:
    if users_match_with_todos.get(f'{u.id}') is None:
        print(f'У пользователя {u.username} нет задач.')
        break
    # Поиск завершенных и оставшихся задач
    true_t = ''
    false_t = ''
    ti = 0
    fi = 0
    for t in users_match_with_todos.get(f'{u.id}'):
        if t.completed:
            true_t += f'\n{t.title}'
            ti += 1
        else:
            false_t += f'\n{t.title}'
            fi += 1
    # Шаблон для записи
    template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
               f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
               f'{ti + fi}\n\n' \
               f'Завершённые задачи ({ti}):{true_t}\n\nОставшиеся задачи (' \
               f'{fi}):{false_t}'
    if true_t is None:
        template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{fi}\n\n' \
                   f'Завершённых задач нет.\n\nОставшиеся задачи (' \
                   f'{fi}):{false_t}'
    if false_t is None:
        template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{ti}\n\n' \
                   f'Завершённые задачи ({ti}):{true_t}\n\nОставшихся задач нет.'
    write_file_with_template(u.username, template)
