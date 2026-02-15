import json
from typing import Any

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType #TODO: replace vkapi to aiohttp

from src.util.logger import Logger
from src.config import settings

class VkListener:
    def __init__(self, vk: Any, long_poll: VkBotLongPoll, logger: Logger):
        self.vk = vk
        self.long_poll = long_poll
        self.logger = logger

    def listen(self):
        target_chat_id = int(settings.VK_CHAT_ID)

        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                obj = self.vk.messages.getByConversationMessageId(
                    peer_id=event.obj['message']['peer_id'],
                    conversation_message_ids=event.obj['message']['conversation_message_id']
                )['items'][0]
                self.logger.message("NEW_VK_MESSAGE", json.dumps(obj, ensure_ascii=False, indent=4))
                if event.obj['message']['peer_id'] == target_chat_id: yield obj