import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import WrongResponseCode, TelegramError

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


def check_tokens():
    """доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    check = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    missing_tokens = {}
    for token_name in check:
        if globals()[token_name] is None:
            missing_tokens.append(token_name)
        if missing_tokens:
            logging.error('Сбой')
            return ValueError('Отсутствует токен')


def send_message(bot, message):
    """Отправляет сообщение."""
    logging.info('Отправляет сообщение.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError as error:
        logging.error(f'Сбой при отправке сообщения: {error}')
        raise TelegramError
    logging.debug(f'Сообщение отправлено: {message}')


def get_api_answer(timestamp):
    """Запрос API."""
    logging.info('Запрос API.')
    timestamp = int(time.time())
    prm_req = {
        'url': ENDPOINT,
        'params': {'from_date': timestamp},
    }
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as error:
        message = (
            'Ошибка отправки сообщения: 200. Запрос: {url}, {params}.'
            ).format(**prm_req)
        raise ConnectionError(str(message, error))
    if response.status_code != HTTPStatus.OK:
        raise WrongResponseCode(
            f'Код ответа API: {response.status_code}'
            f'Причина: {response.reason}. '
            f'Текст: {response.text}.'
        )
    return response.json()


def check_response(response):
    """API на соответствие документации."""
    logging.info('API на соответствие документации.')
    if not isinstance(response, dict):
        raise TypeError('В ответе API ожидается словарь')
    if 'homeworks' not in response:
        raise KeyError('нет ключа homeworks в ответе API')
    if not isinstance(response['homeworks'], list):
        raise TypeError('данные homeworks не являются списком')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает статус о конкретной домашней работе."""
    logging.debug('Создание сообщения')
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name"')
    homework_name = homework['homework_name']
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Получен непредусмотренный статус: "status"')
    verdict = HOMEWORK_VERDICTS[status]
    result = (f'Изменился статус проверки работы "{homework_name}". '
              f'{verdict}')
    logging.debug('Сообщение сформировано')
    return result


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Отсутствует токен. Бот остановлен!'
        logging.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_times = int(time.time())
    previous_message = ''
    message = 'Капитальный сбой работы'
    while True:
        try:
            response = get_api_answer(current_times)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
            else:
                logging.info(message)
                continue
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
            else:
                logging.info(message)
            current_times = response.get(
                'current_date', int(time.time())
            )

        except TelegramError as error:
            message = 'Сообщение не отправлено, временная '
            f'метка не обновлена: {error}'
            logging.error(message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != previous_message:
                send_message(bot, message)
                previous_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=logging.StreamHandler(stream=sys.stdout),
        format='%(asctime)s, %(levelname)s, %(name)s,%(filename)s, '
        '%(funcName)s, %(lineno)s, %(message)s'
    )
    main()
