# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from aiogram import Bot
from src.config import settings

class TgClient:
    def __init__(self):
        self.bot = Bot(token=settings.TG_BOT_TOKEN)

    async def send_text(self, chat_id: str,
                           text: str,
                           **kwargs
                           ):
        return await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            **kwargs
        )

    async def send_photo(self, chat_id: str,
                         photo_url: str,
                         caption: str = "",
                         has_spoiler: bool = False,
                         reply_markup = None):
        return await self.bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            parse_mode="HTML",
            caption=caption,
            has_spoiler=has_spoiler,
            reply_markup=reply_markup
        )

    async def send_video(self, chat_id: str,
                         video_url: str,
                         caption: str = "",
                         supports_streaming: bool = True,
                         duration: int = None,
                         width: int = None, height: int = None,
                         reply_markup = None
                         ):
        return await self.bot.send_video(
            chat_id=chat_id,
            video=video_url,
            caption=caption,
            supports_streaming=supports_streaming,
            duration=duration,
            width=width, height=height,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    async def send_audio(self, chat_id: str,
                         audio_url: str,
                         caption: str = "",
                         performer: str = None,
                         title: str = None,
                         duration: int = None,
                         reply_markup = None
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

    async def send_voice(self, chat_id: str,
                         voice_url: str,
                         caption: str = "",
                         duration: int = None,
                         ):
        return await self.bot.send_voice(
            chat_id=chat_id,
            voice=voice_url,
            caption=caption,
            parse_mode="HTML",
            duration=duration
        )


    async def send_document(self, chat_id: str,
                            document_url: str,
                            caption: str = "",
                            disable_content_type_detection: bool = None
                            ):
        return await self.bot.send_document(
            chat_id=chat_id,
            document=document_url,
            caption=caption,
            parse_mode="HTML",
            disable_content_type_detection=disable_content_type_detection
        )

    async def send_animation(self, chat_id: str,
                             animation_url: str,
                             caption: str = ""
                             ):
        return await self.bot.send_animation(
            chat_id=chat_id,
            animation=animation_url,
            parse_mode="HTML",
            caption=caption
        )

    async def send_media_group(self, chat_id: str, media: list):
        return await self.bot.send_media_group(
            chat_id=chat_id,
            media=media,
        )

    # TODO: add more methods as needed, e.g., send_sticker, send_location, etc and edit methods.