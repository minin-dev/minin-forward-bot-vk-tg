# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from typing import Optional, List, Union
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, ForceReply


class TgSender:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_text(self, chat_id: str, text: str, **kwargs):
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            **kwargs
        )

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: str = "",
        has_spoiler: bool = False,
        reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None
    ):
        return await self.bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode="HTML",
            has_spoiler=has_spoiler,
            reply_markup=reply_markup
        )

    async def send_video(
        self,
        chat_id: str,
        video_url: str,
        caption: str = "",
        supports_streaming: bool = True,
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None
    ):
        return await self.bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=caption,
            supports_streaming=supports_streaming,
            duration=duration,
            width=width,
            height=height,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    async def send_audio(
        self,
        chat_id: str,
        audio_url: str,
        caption: str = "",
        performer: Optional[str] = None,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        reply_markup: Optional[Union[ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, ForceReply]] = None
    ):
        return await self.bot.send_audio(
            chat_id=chat_id,
            audio=audio_url,
            caption=caption,
            performer=performer,
            title=title,
            duration=duration,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    async def send_voice(
        self,
        chat_id: str,
        voice_url: str,
        caption: str = "",
        duration: Optional[int] = None
    ):
        return await self.bot.send_voice(
            chat_id=chat_id,
            voice=voice_url,
            caption=caption,
            parse_mode="HTML",
            duration=duration
        )

    async def send_document(
        self,
        chat_id: str,
        document_url: str,
        caption: str = "",
        disable_content_type_detection: Optional[bool] = None
    ):
        return await self.bot.send_document(
            chat_id=chat_id,
            document=document_url,
            caption=caption,
            parse_mode="HTML",
            disable_content_type_detection=disable_content_type_detection
        )

    async def send_animation(
        self,
        chat_id: str,
        animation_url: str,
        caption: str = ""
    ):
        return await self.bot.send_animation(
            chat_id=chat_id,
            animation=animation_url,
            caption=caption,
            parse_mode="HTML"
        )

    async def send_media_group(self, chat_id: str, media: List):
        return await self.bot.send_media_group(
            chat_id=chat_id,
            media=media,
        )

