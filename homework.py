import logging
import os
import sys
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import EmptyAPI, WrongResponseCode

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(name)s,%(filename)s, '
           '%(funcName)s, %(lineno)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log', 
                              maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

def check_tokens():
    logging.info('Проверка наличия всех токенов')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])

def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')

def get_api_answer(timestamp):
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if response.status_code!=HTTPStatus.OK:
            raise WrongResponseCode(
                f'Код ответа API: {response.status_code}'
                f'Причина: {response.reason}. '
                f'Текст: {response.text}.'
            )
        return response.json()
    
    except Exception as error:
        raise WrongResponseCode(error)

def check_response(response):
    logging.info('Проверка ответа API на корректность')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является dict')
    if 'homeworks' not in response or 'current_date' not in response:
        raise EmptyAPI('Нет ключа homeworks в ответе API')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise KeyError('homeworks не является list')
    return homeworks

def parse_status(homework):
    logger.debug('Создание сообщения')
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name"')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_VERDICTS.keys():
        raise KeyError('Отсутствует ключ "status"')
    verdict = HOMEWORK_VERDICTS[status]
    result = (f'Изменился статус проверки работы "{homework_name}". '
              f'{verdict}')
    logger.debug('Сообщение сформировано')
    return result

def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Токен отсутствует'
        logging.critical(message)
        sys.exit(message)
    current_timestamp = response.get('current_date', current_timestamp)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    error_message = 'Капитальный сбой работы'
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response
            current_timestamp = response.get(
                'current_date', int(time.time())
            )
            if homeworks:
                message = parse_status(homeworks[0])
                time.sleep(RETRY_PERIOD)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message, error)
            if message not in error_message and message==True:
                message = send_message(bot, error_message)
                logger.error(error_message)

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
