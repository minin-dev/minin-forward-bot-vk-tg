# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import asyncio
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

if __name__ == "__main__":
    asyncio.run(main())