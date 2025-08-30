from config import settings
from src.client.tg_client import TgClient
import asyncio

class Sender:
    def __init__(self, tg_client):
        self.tg_client = tg_client

    async def send_message(self, messages: list) -> None:
        for message in messages:
            if message['type'] == 'text':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=message['data']
                )
            elif message['type'] == 'media_group':
                await self.tg_client.send_media_group(
                    chat_id=settings.TG_CHAT_ID,
                    media=message['media'],
                    caption=message.get('caption', "")
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
            elif message['type'] == 'forward':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=f"Forwarded message:\n{message['data']}"
                )