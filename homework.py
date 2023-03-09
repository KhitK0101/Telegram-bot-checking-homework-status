import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import WrongResponseCode

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
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(name)s,%(filename)s, '
           '%(funcName)s, %(lineno)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def check_tokens():
    """доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение отправлено: {message}')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """Запрос API."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if response.status_code != HTTPStatus.OK:
            raise WrongResponseCode(
                f'Код ответа API: {response.status_code}'
                f'Причина: {response.reason}. '
                f'Текст: {response.text}.'
            )
        return response.json()

    except Exception as error:
        raise WrongResponseCode(error)


def check_response(response):
    """API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('В {response} ожидается словарь')
    if response.get('homeworks') is None:
        raise KeyError('Вероятно введены не те переменные')
    elif not isinstance(response['homeworks'], list):
        raise TypeError('homeworks не является list')
    return response['homeworks']


def parse_status(homework):
    """статус конкретной работы."""
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
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_time = int(time.time())
    error_message = 'Капитальный сбой работы'
    while True:
        try:
            response = get_api_answer(current_time)
            homeworks = check_response(response)
            current_time = response.get(
                'current_date', int(time.time())
            )
            if homeworks:
                message = parse_status(homeworks)
                time.sleep(RETRY_PERIOD)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message, error)
            if message not in error_message and message is True:
                message = send_message(bot, error_message)
                logger.error(error_message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
