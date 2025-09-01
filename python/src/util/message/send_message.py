# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import time

from src.config import settings
from aiogram.types import InputMediaPhoto, InputMediaDocument, Message
from src.util.logger.logger import PIMLogger

from src.client.vk_client import VkClient


class Sender:
    def __init__(self, tg_client):
        self.tg_client = tg_client
        self.logger = PIMLogger()

    async def send_message(self, messages: list) -> None:
        message_response = []
        for message in messages:
            if message.get("from_id") is None: continue
            message_data = message['data']
            user = VkClient.get_user_info(message.get("from_id"))
            if message.get("forwarded", False): first_message = f"<blockquote>Пересланное сообщение от: <b>{user.get('name')}</b> </blockquote>\n\n"
            else: first_message = '<blockquote><b>' + user.get("name") + '</b></blockquote>' + "\n\n"
            if message['type'] == 'text':
                message_response.append(await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + '<blockquote>' + message_data['text'] + '</blockquote>'
                ))
            elif message['type'] == 'photo_group':
                for idx, item in enumerate(message_data['media']):
                    if idx == 0 and message_data.get('caption', ""):
                        item['caption'] = first_message + '<blockquote>' + message_data['caption'] + '</blockquote>'
                        item['parse_mode'] = 'HTML'
                media = [
                    InputMediaPhoto(
                        media=item['url'],
                        caption=item.get('caption', None),
                        parse_mode=item.get('parse_mode', None))
                    for item in message_data['media']
                ]

                message_response.append(await self.tg_client.send_media_group(
                    chat_id=settings.TG_CHAT_ID,
                    media=media
                ))
            elif message['type'] == 'video_group':
                for idx, item in enumerate(message_data['media']):
                    if idx == 0 and message_data.get('caption', ""):
                        item['caption'] = first_message + '<blockquote>' + message_data['caption'] + '</blockquote>'
                    else:
                        item['caption'] = '<blockquote>' + item.get('title', '') + '</blockquote>'
                    message_response.append(await self.tg_client.send_text(
                        chat_id=settings.TG_CHAT_ID,
                        text=item['caption'] + f"<blockquote><a href='{item['url']}'>✘ ДЛЯ ПРОСМОТРА ВИДЕО, НАЖМИТИ СЮДА!</a></blockquote>"
                    ))
            elif message['type'] == 'document_group':
                media = []
                for idx, item in enumerate(message_data['documents']):
                    if idx == 0 and message_data.get('caption', ""):
                        item['caption'] = first_message + '<blockquote>' + message_data['caption'] + '</blockquote>'
                    media.append(InputMediaDocument(media=item['url'], caption=item.get('caption', None)))
                try:
                    message_response.append(await self.tg_client.send_media_group(
                        chat_id=settings.TG_CHAT_ID,
                        media=media
                    ))
                except Exception:
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                    buttons = []
                    for doc in message_data.get('documents', []):
                        buttons.append(
                            [InlineKeyboardButton(
                                text=doc.get("title", "Ссылка на документ"),
                                url=doc.get("url")
                            )]
                        )

                    if buttons:
                        caption = message_data.get('caption', "")
                        text = \
                            (f'{first_message} '
                             f'<blockquote>{caption}</blockquote>\n\n '
                             f'<blockquote><b> Прилепленные документы </b></blockquote>') if caption != "" else \
                            (f'{first_message} '
                                f'<blockquote><b> Прилепленные документы </b></blockquote>')

                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        message_response.append(await self.tg_client.send_text(
                            chat_id=settings.TG_CHAT_ID,
                            text=text,
                            reply_markup=keyboard
                        ))
            elif message['type'] == 'photo':
                message_response.append(await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message_data['url'],
                    caption=first_message + '<blockquote>' + message_data.get('caption', "") + '</blockquote>'
                ))
            elif message['type'] == 'voice':
                message_response.append(await self.tg_client.send_voice(
                    chat_id=settings.TG_CHAT_ID,
                    voice_url=message_data['url'],
                    caption=first_message + '<blockquote>' + message_data.get('caption', "") + '</blockquote>',
                    duration=message_data.get('duration', None)
                ))
            elif message['type'] == 'audio':
                caption = '<blockquote>' + message_data.get('caption', "") + '</blockquote>'
                if caption != "": caption = first_message + caption
                message_response.append(await self.tg_client.send_audio(
                    chat_id=settings.TG_CHAT_ID,
                    audio_url=message_data['url'],
                    caption=caption,
                    performer=message_data.get('performer', None),
                    title=message_data.get('title', None),
                    duration=message_data.get('duration', None)
                ))
            elif message['type'] == 'sticker':
                message_response.append(await self.tg_client.send_photo(
                    chat_id=settings.TG_CHAT_ID,
                    photo_url=message_data['url'],
                    caption=first_message
                ))
            elif message['type'] == 'wall':
                message_response.append(await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + f"<blockquote><a href='{message_data['url']}'>✘ ДЛЯ ПРОСМОТРА ВСЕЙ ЗАПИСИ, НАЖМИТИ СЮДА!</a></blockquote>"
                ))
            elif message['type'] == 'poll':
                message_response.append(await self.tg_client.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=first_message + f"<blockquote>Опрос: <b>{message_data.get('question', 'Без названия')}</b></blockquote>\n\n" +
                         "\n".join([f"• {option.get('text', '')} — {option.get('votes', 0)} голосов" for option in message_data.get('options', [])])
                ))
        message_response.append(await self.tg_client.send_text(
            chat_id=settings.TG_CHAT_ID,
            text=f'<tg-spoiler><b>КОНЕЦ СООБЩЕНИЯ - {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}</b></tg-spoiler>'
        ))
        c = 0
        for response in message_response:
            c += 1
            self.logger.send_message(f"SENT_TO_TG [{c}]",  str(response))
        print(self.logger.terminal_cap_generator())