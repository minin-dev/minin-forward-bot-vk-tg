# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import json

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType #TODO: replace vkapi to aiohttp

from src.util.logger.logger import Logger
from src.config import settings

vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, settings.VK_GROUP_ID)

class VkClient:

    def __init__(self):
        self.logger = Logger()

    def listen(self):
        target_chat_id = int(settings.VK_CHAT_ID)
        
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                obj = vk.messages.getByConversationMessageId(
                    peer_id=event.obj['message']['peer_id'],
                    conversation_message_ids=event.obj['message']['conversation_message_id']
                )['items'][0]
                self.logger.message("NEW_VK_MESSAGE", json.dumps(obj, ensure_ascii=False, indent=4))
                if event.obj['message']['peer_id'] == target_chat_id: yield obj

    @staticmethod
    def get_user_info(user_id: int) -> dict:
        user = vk.users.get(user_ids=user_id)[0]
        return {
            "id": user['id'],
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        }
