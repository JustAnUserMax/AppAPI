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
        response = requests.get(path)
        if response.status_code == 200:
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
    else:
        f = open(path, 'w+')
        f.write(temp)
        f.close()


def main():
    # Создание папки tasks
    os.makedirs('./tasks', exist_ok=True)
    # Ссылки для получения json
    todos = 'https://json.medrocket.ru/todos'
    users = 'https://json.medrocket.ru/users'
    # Подключение к сайту и загрузка json
    response_users = Connector.connection(users)
    response_todos = Connector.connection(todos)
    # Словарь для users и todos и списки для хранения данных
    users_match_with_todos = {}
    class_of_users = []
    # Соотнесение пользователя и его задач
    for user in response_users:
        class_of_users.append(JsonLoaderInClass.loader_to_User(user))
        todos_of_the_one_user = []
        for todo in response_todos:
            if todo.get('userId') == user.get('id'):
                todos_of_the_one_user.append(JsonLoaderInClass.loader_to_Todo(todo))
        users_match_with_todos[f'{JsonLoaderInClass.loader_to_User(user).id}'] = todos_of_the_one_user
    # Запись отчётов
    for u in class_of_users:
        if users_match_with_todos.get(f'{u.id}') is None:
            print(f'У пользователя {u.username} нет задач.')
            break
        # Поиск завершенных и оставшихся задач
        true_todo_in_main = ''
        false_todo_in_main = ''
        num_of_true_todos = 0
        num_of_false_todos = 0
        for t in users_match_with_todos.get(f'{u.id}'):
            if t.completed:
                true_todo_in_main += f'\n{t.title}'
                num_of_true_todos += 1
            else:
                false_todo_in_main += f'\n{t.title}'
                num_of_false_todos += 1
        # Шаблон для записи
        template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{num_of_true_todos + num_of_false_todos}\n\n' \
                   f'Завершённые задачи ({num_of_true_todos}):{true_todo_in_main}\n\nОставшиеся задачи (' \
                   f'{num_of_false_todos}):{false_todo_in_main}'
        if true_todo_in_main == '':
            template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
                       f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                       f'{num_of_false_todos}\n\n' \
                       f'Завершённых задач нет.\n\nОставшиеся задачи (' \
                       f'{num_of_false_todos}):{false_todo_in_main}'
        if false_todo_in_main == '':
            template = f'Отчёт для {u.company_name}.\n{u.name} <{u.email}> ' \
                       f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                       f'{num_of_true_todos}\n\n' \
                       f'Завершённые задачи ({num_of_true_todos}):{true_todo_in_main}\n\nОставшихся задач нет.'
        write_file_with_template(u.username, template)


if __name__ == '__main__':
    main()
