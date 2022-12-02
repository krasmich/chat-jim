import sys
import os
import logging
import logging.handlers
from common.variables import LOGGING_LEVEL
sys.path.append('../../')


format_server = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')


path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'server.log')


stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(format_server)
stream_handler.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(format_server)


logger_server = logging.getLogger('server')
logger_server.addHandler(stream_handler)
logger_server.addHandler(LOG_FILE)
logger_server.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    logger_server.critical('Критическая ошибка')
    logger_server.error('Ошибка')
    logger_server.debug('Отладочная информация')
    logger_server.info('Информационное сообщение')
