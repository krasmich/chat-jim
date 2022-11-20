import sys
import json
import socket
import time
import argparse
import logging
import threading
import log.configs.client_log_config
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, \
    TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import receive_message, send_message
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from decor import log

logger_client = logging.getLogger('client')


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
        sys.exit(1)

    return server_address, server_port, client_name


class Client:
    def __init__(self, client_name, server_address, server_port):
        self.client_name = client_name
        self.server_address = server_address
        self.server_port = server_port

    @log
    def help_for_user(self):
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @log
    def presence_message(self, account_name):
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
    def create_message(self, sock, account_name='krasmich'):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды.
        """
        to_user = input('Введите имя получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger_client.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(sock, message_dict)
            logger_client.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            logger_client.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log
    def interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.help_for_user()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.help_for_user()
            elif command == 'exit':
                send_message(sock, self.exit_message(username))
                print('Завершение соединения.')
                logger_client.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @log
    def processing_answer(self, message):
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
    def message_from_server(self, sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = receive_message(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    logger_client.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                       f'\n{message[MESSAGE_TEXT]}')
                else:
                    logger_client.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                logger_client.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                logger_client.critical(f'Потеряно соединение с сервером.')
                break

    @log
    def exit_message(self, account_name):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    def processing_request_client(self):
        """
        Функция обработки параметров командной строки
        """
        print('Консольный месседжер. Клиентский модуль.')

        self.server_address, self.server_port, self.client_name = create_arg_parser()

        if not self.client_name:
            self.client_name = input('Введите имя пользователя: ')

        logger_client.info(
            f'Запущен клиент с парамертами: адрес сервера: {self.server_address}, '
            f'порт: {self.server_port}, режим работы: {self.client_name}')

        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.server_address, self.server_port))
            send_message(transport, self.presence_message(self.client_name))
            answer = self.processing_answer(receive_message(transport))
            logger_client.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            logger_client.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            logger_client.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            logger_client.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            logger_client.critical(
                f'Не удалось подключиться к серверу {self.server_address}:{self.server_port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            receiver = threading.Thread(target=self.message_from_server, args=(transport, self.client_name))
            receiver.daemon = True
            receiver.start()

            user_interface = threading.Thread(target=self.interactive, args=(transport, self.client_name))
            user_interface.daemon = True
            user_interface.start()
            logger_client.debug('Запущены процессы')

            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break


def main():
    client_name, server_address, server_port = create_arg_parser()
    client = Client(client_name, server_address, server_port)
    client.processing_request_client()


if __name__ == '__main__':
    main()
