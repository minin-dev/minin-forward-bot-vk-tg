# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from aiogram import Bot

from src.config import settings
from .sender import TgSender


class TgClient:
    def __init__(self):
        self.bot = Bot(token=settings.TG_BOT_TOKEN)
        self.sender = TgSender(self.bot)