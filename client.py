import sys
import json
import argparse
import socket
import sys
import threading
import logging
import time
import dis
import log.configs.client_log_config
from common.utils import *
from common.variables import *
from decor import log
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from metaclasses import ClientVerifier

logger_client = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды.
        """
        to = input('Введите имя получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger_client.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            logger_client.info(f'Отправлено сообщение для пользователя {to}')
        except:
            logger_client.critical('Потеряно соединение с сервером.')
            exit(1)

    def interactive(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.help_for_user()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.help_for_user()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.exit_message())
                except:
                    pass
                print('Завершение соединения.')
                logger_client.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def help_for_user(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def message_from_server(self):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = receive_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger_client.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                       f'\n{message[MESSAGE_TEXT]}')
                else:
                    logger_client.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                logger_client.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger_client.critical(f'Потеряно соединение с сервером.')
                break


@log
def presence_message(account_name):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger_client.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def processing_answer(message):
    """
    Функция разбирает ответ сервера
    """
    logger_client.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        logger_client.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


def main():
    print('Консольный месседжер. Клиентский модуль.')

    server_address, server_port, client_name = create_arg_parser()

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    logger_client.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, режим работы: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, presence_message(client_name))
        answer = processing_answer(receive_message(transport))
        logger_client.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        logger_client.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger_client.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger_client.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except ConnectionRefusedError:
        logger_client.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.start()

        user_interface = ClientSender(client_name, transport)
        user_interface.daemon = True
        user_interface.start()
        logger_client.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
