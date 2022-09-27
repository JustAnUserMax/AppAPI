import datetime
import os.path
import re
import requests
from sys import platform


# Класс для записи пользователей
class User(object):
    def __init__(self, _id, name, username, email, company_name, true_todos, false_todos, num_of_true_todos,
                 num_of_false_todos):
        self.id = _id
        self.name = name
        self.username = username
        self.email = email
        self.company_name = company_name
        self.true_todos = true_todos
        self.false_todos = false_todos
        self.num_of_true_todos = num_of_true_todos
        self.num_of_false_todos = num_of_false_todos


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
    def loader_to_User(response, true_todos, false_todos, num_of_true_todos, num_of_false_todos):
        # Проверка валидности почты
        if Validator.is_valid_email(response.get('email')):
            return User(
                response.get('id'),
                response.get('name'),
                response.get('username'),
                response.get('email'),
                response.get('company').get('name'),
                true_todos,
                false_todos,
                num_of_true_todos,
                num_of_false_todos
            )
        else:
            return Exception

    # Загрузка из json в Td
    @staticmethod
    def loader_to_Todo(response):
        title = ''
        # Обрезка строки до 48 символов
        if response.get('title') is not None and len(response.get('title')) > 48:
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
def write_file(path, temp):
    f = open(path, 'w+')
    f.write(temp)
    f.close()


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
                write_file(path, temp)
            else:
                os.rename(path, path_to_old_file_for_linux)
                write_file(path, temp)
        else:
            # Проверка на то, есть ли старый отчёт (возможно использование скрипта в ту же минуту)
            if os.path.isfile(path_to_old_file_for_windows):
                os.rename(path, f'./tasks/old_{username}_{today.strftime("%Y-%m-%d")}T'
                                f'{today.strftime("%H.%M.%S")}.txt')
                write_file(path, temp)
            else:
                os.rename(path, path_to_old_file_for_windows)
                write_file(path, temp)
    else:
        write_file(path, temp)


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
    list_of_todos = []
    for todo in response_todos:
        list_of_todos.append(JsonLoaderInClass.loader_to_Todo(todo))
    list_of_users = []
    # Соотнесение пользователя и его задач
    for user in response_users:
        todos_of_the_one_user = list(filter(lambda item: item.user_id == user.get('id'), list_of_todos))
        # Контроль filter
        if todos_of_the_one_user[0].user_id != user.get('id'):
            break
        true_todos = list(filter(lambda todo: todo.completed is True, todos_of_the_one_user))
        false_todos = list(filter(lambda todo: todo.completed is False, todos_of_the_one_user))
        # Проверка на то, какие конкретно существуют задачи
        if true_todos[0].completed is True:
            true_todos = list(map(lambda todo: todo.title, true_todos))
            num_of_true_todos = len(true_todos)
            true_todos = str(true_todos).strip('[]').replace(', ', '\n').replace("'", '')
        else:
            true_todos = None
            num_of_true_todos = 0
        if false_todos[0].completed is False:
            false_todos = list(map(lambda todo: todo.title, false_todos))
            num_of_false_todos = len(false_todos)
            false_todos = str(false_todos).strip('[]').replace(', ', '\n').replace("'", '')
        else:
            false_todos = None
            num_of_false_todos = 0
        list_of_users.append(JsonLoaderInClass.loader_to_User(user,
                                                              true_todos,
                                                              false_todos,
                                                              num_of_true_todos,
                                                              num_of_false_todos
                                                              ))
        users_match_with_todos[f'{list_of_users[-1].id}'] = todos_of_the_one_user
    # Запись отчетов
    for user in list_of_users:
        if users_match_with_todos.get(f'{user.id}') is None:
            print(f'У пользователя {user.username} нет задач.')
            break
        # Шаблон для записи
        template = f'Отчёт для {user.company_name}.\n{user.name} <{user.email}> ' \
                   f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                   f'{user.num_of_true_todos + user.num_of_false_todos}\n\n' \
                   f'Завершённые задачи ({user.num_of_true_todos}):\n{user.true_todos}\n\nОставшиеся задачи (' \
                   f'{user.num_of_false_todos}):\n{user.false_todos}'
        if user.true_todos is None:
            template = f'Отчёт для {user.company_name}.\n{user.name} <{user.email}> ' \
                       f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                       f'{user.num_of_false_todos}\n\n' \
                       f'Завершённых задач нет.\n\nОставшиеся задачи (' \
                       f'{user.num_of_false_todos}):\n{user.false_todos}'
        if user.false_todos is None:
            template = f'Отчёт для {user.company_name}.\n{user.name} <{user.email}> ' \
                       f'{today.strftime("%Y.%m.%d")} {today.strftime("%H:%M")}\nВсего задач: ' \
                       f'{user.num_of_true_todos}\n\n' \
                       f'Завершённые задачи ({user.num_of_true_todos}):\n{user.true_todos}\n\nОставшихся задач нет.'
        write_file_with_template(user.username, template)


if __name__ == '__main__':
    main()
