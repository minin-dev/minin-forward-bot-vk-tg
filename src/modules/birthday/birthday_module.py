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

from src.config.config import token, chat_id, bd_dates
from src.console.console_messages import send_message

telegram_bot_token = token['tg']
telegram_chat_id = chat_id['tg']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def ensure_directory_exists(path):
    """Ensure that directory exists, create if not"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

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
                if type(bd_dates[current_date]) is list:
                    response = requests.post(
                            f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                            data={
                                "chat_id": telegram_chat_id,
                                "text": (
                                    f"🎉 <b>Сегодня особенный день!</b> 🎉\n\n"
                                    f"Поздравляем с Днём Рождения замечательных людей — <b>{', '.join(bd_dates[current_date])}</b>! 🥳🎂\n\n"
                                    f"✨ Желаем вам счастья, крепкого здоровья и исполнения всех желаний!\n"
                                    f"🚀 Пусть каждый день приносит радость, новые возможности и только приятные сюрпризы.\n"
                                    f"💡 Оставайтесь такими же яркими, талантливыми и неповторимыми!\n\n"
                                    f"<i>Пусть этот год станет для вас лучшим!</i> 🎊"
                                ),
                                "parse_mode": "HTML"
                            },
                            timeout=10
                        )
                    
                else: 
                    response = requests.post(
                            f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                            data={
                                "chat_id": telegram_chat_id,
                                "text": (
                                    f"🎉 <b>Сегодня особенный день!</b> 🎉\n\n"
                                    f"Поздравляем с Днём Рождения замечательного человека — <b>{bd_dates[current_date]}</b>! 🥳🎂\n\n"
                                    f"✨ Желаем вам счастья, крепкого здоровья и исполнения всех желаний!\n"
                                    f"🚀 Пусть каждый день приносит радость, новые возможности и только приятные сюрпризы.\n"
                                    f"💡 Оставайся таким же ярким, талантливым и неповторимым!\n\n"
                                    f"<i>Пусть этот год станет для тебя лучшим!</i> 🎊"
                                ),
                                "parse_mode": "HTML"
                            },
                            timeout=10
                        )
                
                send_message("BIRTHDAY_MODULE_RESPONSE", response.json())

                content.seek(0)
                content.write(current_date)
                content.truncate()

    except Exception as e:
        logger.error(f"Error in birthday function: {e}")

if __name__ == "__main__":
    logger.info("Birthday module has been started!")
    while True:
        try:
            birthday()
            time.sleep(3600*24)
        except Exception as e:
            logger.error(f"Error in birthday module main loop: {e}")
            time.sleep(300)
