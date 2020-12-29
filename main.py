import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    filename='main.log',
    format='!levelname!: %(asctime)s %(message)s'
)

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_GET_HOMEWORK = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS_FOR_YANDEX = {
    'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',
}


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    form_date_for_homework_get = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(
        URL_GET_HOMEWORK,
        headers=HEADERS_FOR_YANDEX,
        params=form_date_for_homework_get
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            bot_client_telegram = telegram.Bot(token=TELEGRAM_TOKEN)
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client_telegram
                )
            current_timestamp = new_homework.get('current_date', current_timestamp)
            time.sleep(300)

        except Exception as e:
            logging.error(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
