import sys
import os
import logging
from common.variables import LOGGING_LEVEL

# sys.path.append('../../')

format_client = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

path = 'D:/GB/3_quarter/Databases_and_PyQT/client-server-jim/log/log_files'


path = os.path.join(path, 'client.log')


stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(format_client)
stream_handler.setLevel(logging.ERROR)
LOG_FILE = logging.FileHandler(path, encoding='utf8')
LOG_FILE.setFormatter(format_client)

logger_client = logging.getLogger('client')
logger_client.addHandler(stream_handler)
logger_client.addHandler(LOG_FILE)
logger_client.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    logger_client.critical('Критическая ошибка')
    logger_client.error('Ошибка')
    logger_client.debug('Отладочная информация')
    logger_client.info('Информационное сообщение')
