import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    filename='main.log', filemode='a',
    format='-'*50 + '\n!%(levelname)s!: %(asctime)s: %(message)s\n' + '-'*50
)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_GET_HOMEWORK = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS_FOR_YANDEX = {
    'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
}


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status == 'reviewing':
        return f'У вас начали проверять работу "{homework_name}"!'
    elif status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:
        return 'Пришёл неверный статус ответа от Яндекс Практикума'

    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = int(time.time()) if current_timestamp is None else current_timestamp
    form_date_for_homework_get = {
        'from_date': current_timestamp
    }

    try:
        homework_statuses = requests.get(
            URL_GET_HOMEWORK,
            headers=HEADERS_FOR_YANDEX,
            params=form_date_for_homework_get
        )

        return homework_statuses.json()

    except requests.exceptions.ConnectionError as e:
        logging.error(f'Не удаётся установить соединение: {e}')
    except ValueError as e:
        logging.error('Возвращается битый json  в функции получания статуса дз')

    return {}


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            bot_client_telegram = telegram.Bot(token=TELEGRAM_TOKEN)
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                message = parse_homework_status(new_homework.get('homeworks')[0])
                send_message(
                    message,
                    bot_client_telegram
                )
                logging.info(f'Удачно отправил сообщение\n\n{message}')
            current_timestamp = new_homework.get('current_date', current_timestamp)
            time.sleep(60)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
