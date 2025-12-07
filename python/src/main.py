# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import asyncio
import json
from datetime import datetime
from pathlib import Path
from client.vk_client import VkClient
from client.tg_client import TgClient
from src.config import settings
from src.util.message.message_processor import VkMessageProcessor
from src.util.message.send_message import Sender
from src.util.logger.logger import PIMLogger

async def main():
    logger = PIMLogger()
    vk_client = VkClient()
    tg_client = TgClient()
    sender = Sender(tg_client)
    vk_message_processor = VkMessageProcessor()

    try:
        logger.start_message(
            time=asyncio.get_event_loop().time(),
            tg_chat_id=settings.TG_CHAT_ID,
            vk_chat_id=settings.VK_CHAT_ID
        )
        for message in vk_client.listen():
            await sender.send_message(vk_message_processor.process_message(message))
    finally:
        await tg_client.bot.session.close()

async def birthday_module():
    tg_client = TgClient()
    try:
        data_path = Path(__file__).parent.parent / "data" / "birthdays.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        today = datetime.now()
        today_str = today.strftime("%m-%d")

        for person in data.get("birthdays", []):
            birth_date = datetime.strptime(person["date"], "%Y-%m-%d")
            birth_str = birth_date.strftime("%m-%d")

            if birth_str == today_str:
                age = today.year - birth_date.year
                message = f"🎉 Сегодня день рождения у {person['name']}! Исполняется {age} лет!"
                await tg_client.send_text(chat_id=settings.TG_CHAT_ID, text=message)
    finally:
        await tg_client.bot.session.close()

if __name__ == "__main__":
    asyncio.run(birthday_module())
    asyncio.run(main())
