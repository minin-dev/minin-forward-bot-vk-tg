import time

from config import settings
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from src.client.tg_client import TgClient
import asyncio

from src.client.vk_client import VkClient


class Sender:
    def __init__(self, tg_client):
        self.tg_client = tg_client

    async def send_message(self, messages: list) -> None:
        for message in messages:
            print(message)
            if message.get("from_id") is None: continue
            message_data = message['data']
            user = VkClient.get_user_info(message.get("from_id"))
            if message.get("forwarded", False): first_message = f"<blockquote>Пересланное сообщение от: <b>{user.get('name')}</b> </blockquote>\n\n"
            else: first_message = '<blockquote><b>' + user.get("name") + '</b></blockquote>' + "\n\n"
            if message['type'] == 'text':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + '<blockquote>' + message_data['text'] + '</blockquote>'
                )
            elif message['type'] == 'media_group':
                # TODO: documents
                for attachment in message_data['media']:
                    if attachment['type'] == 'photo':
                        attachment['type'] = 'photo'
                        attachment['media'] = attachment.pop('url')
                    elif attachment['type'] == 'video':
                        attachment['type'] = 'video'
                        attachment['media'] = attachment.pop('url')
                media = []
                for idx, item in enumerate(message_data['media']):
                    if idx == 0 and message_data.get('caption', ""):
                        item['caption'] = first_message + '<blockquote>' + message_data['caption'] + '</blockquote>'
                        item['parse_mode'] = "HTML"
                    media.append(InputMediaPhoto(**item) if item['type'] == 'photo' else InputMediaVideo(**item))

                await self.tg_client.send_media_group(
                    chat_id=settings.TG_CHAT_ID,
                    media=media
                )
            elif message['type'] == 'photo':
                await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message_data['url'],
                    caption=first_message + '<blockquote>' + message_data.get('caption', "") + '</blockquote>'
                )
            elif message['type'] == 'voice':
                await self.tg_client.send_voice(
                    chat_id=settings.TG_CHAT_ID,
                    voice_url=message_data['url'],
                    caption=first_message + '<blockquote>' + message_data.get('caption', "") + '</blockquote>',
                    duration=message_data.get('duration', None)
                )
            elif message['type'] == 'audio':
                caption = '<blockquote>' + message_data.get('caption', "") + '</blockquote>'
                if caption != "": caption = first_message + caption
                await self.tg_client.send_audio(
                    chat_id=settings.TG_CHAT_ID,
                    audio_url=message_data['url'],
                    caption=caption,
                    performer=message_data.get('performer', None),
                    title=message_data.get('title', None),
                    duration=message_data.get('duration', None)
                )
            elif message['type'] == 'document':
                try:
                    await self.tg_client.send_document(
                        chat_id=settings.TG_CHAT_ID,
                        document_url=message_data.get('url'),
                        caption=first_message + '<blockquote>' + message_data.get('caption') + '</blockquote>'
                    )
                except Exception:
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text=message["data"]["title"], url=message_data.get('url'))]
                        ]
                    )
                    await self.tg_client.send_text(
                        chat_id=settings.TG_CHAT_ID,
                        text=first_message + '<blockquote>' + message_data.get('caption') + '</blockquote>',
                        reply_markup=keyboard
                    )
            elif message['type'] == 'sticker':
                await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message_data['url']
                )
            elif message['type'] == 'wall':
                await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + f"<blockquote><a href='{message_data['url']}'>✘ ДЛЯ ПРОСМОТРА ВСЕЙ ЗАПИСИ, НАЖМИТИ СЮДА!</a></blockquote>"
                )
        await self.tg_client.send_text(
            chat_id=settings.TG_CHAT_ID,
            text=f'<tg-spoiler><b>КОНЕЦ СООБЩЕНИЯ - {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</b></tg-spoiler>'
        )
