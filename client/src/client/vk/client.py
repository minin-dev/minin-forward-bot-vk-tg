# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import json

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType #TODO: replace vkapi to aiohttp

from src.util.logger import Logger
from src.config import settings

from .listener import VkListener


class VkClient:

    def __init__(self):
        self.vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
        self.vk = self.vk_session.get_api()
        self.long_poll = VkBotLongPoll(self.vk_session, settings.VK_GROUP_ID)
        self.logger = Logger()

        self.listener = VkListener(self.vk, self.long_poll, self.logger)

    def get_user_info(self, user_id: int) -> dict:
        user = self.vk.users.get(user_ids=user_id)[0]
        return {
            "id": user['id'],
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        }
