import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    filename='main.log', filemode='w',
    format='%(levelname)s: %(asctime)s: %(message)s'
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
    verdicts = {
        'reviewing': f'У вас начали проверять работу!',
        'rejected': 'К сожалению в работе нашлись ошибки =(',
        'approved': 'Ревью пройдено!'
    }
    errors = {
        'status': 'Пришёл неверный статус ответа от Яндекс Практикума',
        'homework_name': 'Пришло неверное имя домашки от Яндекс Практикума'
    }

    if status not in verdicts.keys():
        logging.error(errors['status'])

        return errors['status']
    if homework_name is None:
        logging.error(errors['homework_name'])

        return errors['homework_name']

    verdict = verdicts[status]
    if (status == 'rejected') or (status == 'approved'):
        comment = homework.get('reviewer_comment')
        comment = ''
        if comment:
            verdict += f'\n\nКомментарий: {comment}'
        else:
            verdict += '\n\nБез комментариев.'

    return f'Статус проверки  работы: "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    current_timestamp = current_timestamp or int(time.time())
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
