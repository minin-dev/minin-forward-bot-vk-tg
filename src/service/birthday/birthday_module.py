# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
import datetime
import requests
import pytz
import time
import logging

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from src.module.llm.groq_manager import BirthdayGreetingGenerator
from src.config.config import token, chat_id, bd_dates
from src.module.logs.logger import send_message
from src.service.metrics import BirthdayMetrics

telegram_bot_token = token['tg']
telegram_chat_id = chat_id['tg']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

generator = BirthdayGreetingGenerator()

def ensure_directory_exists(path):
    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

def birthday(current_date=None):
    try:
        if current_date is None:
            msk_time = datetime.datetime.now(pytz.timezone("Europe/Moscow"))
            current_date = msk_time.strftime('%m-%d')

        data_file = 'data/date_checker.txt'
        ensure_directory_exists(data_file)

        if not os.path.exists(data_file):
            with open(data_file, 'w') as f:
                f.write("")

        with open(data_file, 'r+') as content:
            last_date = content.read().strip()

            if current_date in bd_dates and last_date != current_date:
                if isinstance(bd_dates[current_date], str):
                    fio = bd_dates[current_date].split()
                    if len(fio) != 3:
                        logger.error(f"Некорректный формат ФИО для даты {current_date}: {bd_dates[current_date]}")
                        return
                    first_name, last_name, patronymic = fio
                    birthdate = datetime.datetime.now().strftime('%Y-%m-%d')
                    greeting_text = generator.generate(first_name, last_name, patronymic, birthdate)
                elif isinstance(bd_dates[current_date], list):
                    fio_list = [i.split() for i in bd_dates[current_date]]
                    if not all(len(i) == 3 for i in fio_list):
                        logger.error(f"Некорректный формат ФИО для нескольких именинников на дату {current_date}: {bd_dates[current_date]}")
                        return
                    first_names = [i[0] for i in fio_list]
                    last_names = [i[1] for i in fio_list]
                    patronymics = [i[2] for i in fio_list]
                    birthdate = datetime.datetime.now().strftime('%Y-%m-%d')
                    greeting_text = generator.generate(first_names, last_names, patronymics, birthdate)
                else:
                    logger.error(f"Некорректный тип значения bd_dates[{current_date}]: {type(bd_dates[current_date])}")
                    return

                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                        "chat_id": telegram_chat_id,
                        "text": greeting_text,
                        "parse_mode": "HTML"
                    },
                    timeout=10
                )

                send_message("BIRTHDAY_MODULE_RESPONSE", response.json())

                if response.status_code == 200:
                    BirthdayMetrics.BIRTHDAY_SENT.inc()
                else:
                    BirthdayMetrics.handle_error(f"Failed to send birthday message: {response.text}")
                    logger.error(f"Failed to send birthday message: {response.text}")

                content.seek(0)
                content.write(current_date)
                content.truncate()

    except Exception as e:
        BirthdayMetrics.handle_error(f"Error in birthday function: {e}")
        logger.error(f"Error in birthday function: {e}")

if __name__ == "__main__":
    logger.info("Birthday module has been started!")
    BirthdayMetrics.start_metrics()
    while True:
        try:
            birthday()
            time.sleep(100)
        except Exception as e:
            logger.error(f"Error in birthday module main loop: {e}")
            time.sleep(300)
