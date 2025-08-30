from config import settings
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from src.client.tg_client import TgClient
import asyncio

from src.client.vk_client import VkClient


class Sender:
    def __init__(self, tg_client):
        self.tg_client = tg_client

    async def send_message(self, messages: list) -> None:
        first_message = ""
        for message in messages:
            user = VkClient.get_user_info(message.get("from_id"))
            if message['type'] == 'text':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + user.get("name") + "\n\n" + message['data']
                )
            elif message['type'] == 'media_group':
                # TODO: documents
                for attachment in message['media']:
                    if attachment['type'] == 'photo':
                        attachment['type'] = 'photo'
                        attachment['media'] = attachment.pop('url')
                    elif attachment['type'] == 'video':
                        attachment['type'] = 'video'
                        attachment['media'] = attachment.pop('url')
                media = []
                for idx, item in enumerate(message['media']):
                    if idx == 0 and message.get('caption', ""):
                        item['caption'] = message['caption']
                    media.append(InputMediaPhoto(**item) if item['type'] == 'photo' else InputMediaVideo(**item))

                await self.tg_client.send_media_group(
                    chat_id=settings.TG_CHAT_ID,
                    media=media
                )
            elif message['type'] == 'photo':
                await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message['data'],
                    caption=message.get('caption', "")
                )
            elif message['type'] == 'voice':
                await self.tg_client.send_voice(
                    chat_id=settings.TG_CHAT_ID,
                    voice_url=message['data']['url'],
                    caption=message.get('caption', ""),
                    duration=message['data'].get('duration', None)
                )
            elif message['type'] == 'audio':
                await self.tg_client.send_audio(
                    chat_id=settings.TG_CHAT_ID,
                    audio_url=message['data']['url'],
                    caption=message.get('caption', ""),
                    performer=message['data'].get('performer', None),
                    title=message['data'].get('title', None),
                    duration=message['data'].get('duration', None)
                )
            elif message['type'] == 'document':
                await self.tg_client.send_document(
                    chat_id=settings.TG_CHAT_ID,
                    document_url=message['data'],
                    caption=message.get('caption', "")
                )
            elif message['type'] == 'sticker':
                await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message['data']
                )
            elif message['type'] == 'wall':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=f"Wall post: {message['data']}"
                )

            first_message = f"Пересланное сообщение от "