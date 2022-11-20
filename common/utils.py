import json

from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from errors import IncorrectDataRecivedError, NonDictInputError
from decor import log


@log
def receive_message(sock):
    """
    Функция приёма и декодирования сообщения
    принимает байты выдаёт словарь, если принято что-то другое отдаёт ошибку значения
    """
    encoded_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    """
    Функция кодирования и отправки сообщения
    принимает словарь и отправляет его
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
