# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import time

from aiogram.types import (
    InputMediaPhoto,
    InputMediaDocument,
    Message
)

from src.util.logger import Logger
from src.client import VkClient
from src.config import settings

class TgMessageProcessor:
    def __init__(self, tg_client, vk_client: VkClient):
        self.tg_client = tg_client
        self.vk_client = vk_client
        self.logger = Logger()

    async def send_message(self, messages: list) -> None:
        message_response = []
        for message in messages:
            if not message.get("from_id"):
                continue

            user_info = self.vk_client.get_user_info(message["from_id"])
            username = user_info.get("name", "Неизвестный")

            header_text = self._create_header(username, message.get("forwarded", False))
            message_data = message["data"]
            message_type = message["type"]

            response = await self._dispatch_message(message_type, message_data, header_text)
            if response:
                message_response.append(response)

        for i, response in enumerate(message_response, start=1):
            self.logger.message(f"SENT_TO_TG [{i}]", str(response))

        print(self.logger.terminal_cap_generator())

    def _create_header(self, username: str, is_forwarded: bool) -> str:
        prefix = 'Пересланное сообщение от: ' if is_forwarded else ''
        return f"<blockquote>{prefix}<b>{username}</b></blockquote>\n\n"

    async def _dispatch_message(self, msg_type: str, data: dict, header: str):
        if msg_type == 'text':
            return await self._handle_text(data, header)
        elif msg_type == 'photo_group':
            return await self._handle_photo_group(data, header)
        elif msg_type == 'video_group':
            return await self._handle_video_group(data, header)
        elif msg_type == 'document_group':
            return await self._handle_document_group(data, header)
        elif msg_type == 'photo':
            return await self._handle_photo(data, header)
        elif msg_type == 'voice':
            return await self._handle_voice(data, header)
        elif msg_type == 'audio':
            return await self._handle_audio(data, header)
        elif msg_type == 'sticker':
            return await self._handle_sticker(data, header)
        elif msg_type == 'wall':
            return await self._handle_wall(data, header)
        elif msg_type == 'poll':
            return await self._handle_poll(data, header)
        return None

    async def _handle_text(self, data: dict, header: str):
        text = f"{header}<blockquote>{data['text']}</blockquote>"
        return await self.tg_client.sender.send_text(
            chat_id=settings.TG_CHAT_ID,
            text=text
        )

    async def _handle_photo_group(self, data: dict, header: str):
        media_group = []
        for idx, item in enumerate(data['media']):
            caption = None
            if idx == 0 and data.get('caption'):
                caption = f"{header}<blockquote>{data['caption']}</blockquote>"
                item['parse_mode'] = 'HTML'

            media_group.append(
                InputMediaPhoto(
                    media=item['url'],
                    caption=caption or item.get('caption'),
                    parse_mode=item.get('parse_mode')
                )
            )

        return await self.tg_client.sender.send_media_group(
            chat_id=settings.TG_CHAT_ID,
            media=media_group
        )

    async def _handle_video_group(self, data: dict, header: str):
        responses = []
        for idx, item in enumerate(data['media']):
            if idx == 0 and data.get('caption'):
                base_caption = f"{header}<blockquote>{data['caption']}</blockquote>"
            else:
                base_caption = f"<blockquote>{item.get('title', '')}</blockquote>"

            full_text = f"{base_caption}<blockquote><a href='{item['url']}'>✘ ДЛЯ ПРОСМОТРА ВИДЕО, НАЖМИТЕ СЮДА!</a></blockquote>"

            resp = await self.tg_client.sender.send_text(
                chat_id=settings.TG_CHAT_ID,
                text=full_text
            )
            responses.append(resp)
        return responses[-1] if responses else None

    async def _handle_document_group(self, data: dict, header: str):
        media_group = []
        for idx, item in enumerate(data['documents']):
            caption = None
            if idx == 0 and data.get('caption'):
                caption = f"{header}<blockquote>{data['caption']}</blockquote>"

            media_group.append(
                InputMediaDocument(
                    media=item['url'],
                    caption=caption
                )
            )

        try:
            return await self.tg_client.sender.send_media_group(
                chat_id=settings.TG_CHAT_ID,
                media=media_group
            )
        except Exception:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            buttons = [
                [InlineKeyboardButton(
                    text=doc.get("title", "Ссылка на документ"),
                    url=doc.get("url")
                )] for doc in data.get('documents', [])
            ]

            caption = data.get('caption', "")
            doc_header = "<blockquote><b> Прикрепленные документы </b></blockquote>"

            if caption:
                text = f"{header} <blockquote>{caption}</blockquote>\n\n {doc_header}"
            else:
                text = f"{header} {doc_header}"

            if buttons:
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                return await self.tg_client.sender.send_text(
                    chat_id=settings.TG_CHAT_ID,
                    text=text,
                    reply_markup=keyboard
                )
            return None

    async def _handle_photo(self, data: dict, header: str):
        caption = f"{header}<blockquote>{data.get('caption', '')}</blockquote>"
        return await self.tg_client.sender.send_photo(
            chat_id=settings.TG_CHAT_ID,
            photo_url=data['url'],
            caption=caption
        )

    async def _handle_voice(self, data: dict, header: str):
        caption = f"{header}<blockquote>{data.get('caption', '')}</blockquote>"
        return await self.tg_client.sender.send_voice(
            chat_id=settings.TG_CHAT_ID,
            voice_url=data['url'],
            caption=caption,
            duration=data.get('duration')
        )

    async def _handle_audio(self, data: dict, header: str):
        raw_caption = data.get('caption', '')
        caption = f"<blockquote>{raw_caption}</blockquote>"
        if raw_caption:
            caption = header + caption

        return await self.tg_client.sender.send_audio(
            chat_id=settings.TG_CHAT_ID,
            audio_url=data['url'],
            caption=caption,
            performer=data.get('performer'),
            title=data.get('title'),
            duration=data.get('duration')
        )

    async def _handle_sticker(self, data: dict, header: str):
        return await self.tg_client.sender.send_photo(
            chat_id=settings.TG_CHAT_ID,
            photo_url=data['url'],
            caption=header
        )

    async def _handle_wall(self, data: dict, header: str):
        text = f"{header}<blockquote><a href='{data['url']}'>✘ ДЛЯ ПРОСМОТРА ВСЕЙ ЗАПИСИ, НАЖМИТЕ СЮДА!</a></blockquote>"
        return await self.tg_client.sender.send_text(
            chat_id=settings.TG_CHAT_ID,
            text=text
        )

    async def _handle_poll(self, data: dict, header: str):
        options = "\n".join([f"• {opt.get('text', '')} — {opt.get('votes', 0)} голосов"
                           for opt in data.get('options', [])])
        text = (f"{header}<blockquote>Опрос: <b>{data.get('question', 'Без названия')}</b></blockquote>\n\n"
                f"{options}")
        return await self.tg_client.sender.send_text(
            chat_id=settings.TG_CHAT_ID,
            text=text
        )
