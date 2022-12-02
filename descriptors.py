import sys
import logging
logger = logging.getLogger('server')


class PortDescriptor:
    """
    Класс - дескриптор для номера порта.
    Позволяет использовать только порты с 1023 по 65536.
    При попытке установить неподходящий номер порта генерирует исключение.
    """

    def __set__(self, instance, value):
        try:
            value = int(value)
        except ValueError:
            logger.error(f"Не верный  тип значения порта: {value}")
            sys.exit(1)
        if value < 1024 or value > 65535:
            logger.error(f"Значение порта {value} Не находится в диапазоне 1025 - 65535.")
            sys.exit(1)
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr
