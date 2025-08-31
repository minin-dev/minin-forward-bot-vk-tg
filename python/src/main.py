import asyncio
from client.vk_client import VkClient
from client.tg_client import TgClient
from util.message_processor import VkMessageProcessor
from util.send_message import Sender

async def main():
    vk_client = VkClient()
    tg_client = TgClient()
    sender = Sender(tg_client)
    vk_message_processor = VkMessageProcessor()

    try:
        for message in vk_client.listen():
            await sender.send_message(vk_message_processor.process_message(message))
    finally:
        await tg_client.bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())