# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
import datetime
import logging
import time
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, project_root)

from src.config.config import token, chat_id
from src.modules.event.handle_func import handle_text, handler, clear_processed_messages_cache
from src.console.console_messages import hello_message, event_message
from src.modules.metrics import EventMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    try:
        vk_session = vk_api.VkApi(token = token['vk'])
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, chat_id['vk'])

        hello_message(datetime.datetime.now(), chat_id['tg'], chat_id['vk'])

        message_counter = 0
        
        while True:
            try:
                for event in longpoll.listen():
                    try:
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            EventMetrics.EVENT_COUNT.inc()
                            message_counter += 1

                            if message_counter >= 100:
                                clear_processed_messages_cache()
                                message_counter = 0
                                
                            message_package = {
                                'author': f"{vk.users.get(user_ids=event.obj.message['from_id'])[0]['first_name']} {vk.users.get(user_ids=event.obj.message['from_id'])[0]['last_name']}",
                                'object': vk.messages.getByConversationMessageId(peer_id=event.obj['message']['peer_id'], conversation_message_ids=event.obj['message']['conversation_message_id'])['items'][0]
                            }
                            
                            event_message(f"[HANDLE_EVENT_VK] {datetime.datetime.now()}", message_package['object'])

                            def main_forward(message):
                                if "text" in message and message["text"]:
                                    check_attacment = False
                                    if "attachments" in message:
                                        for attachment in message["attachments"]:
                                            if "photo" in attachment:
                                                check_attacment = True
                                    if not check_attacment:
                                        handle_text(message_package['author'] + " ✉", message["text"])
                                handler(message)

                            main_forward(message_package['object'])
                    except Exception as e:
                        EventMetrics.handle_error(f"Error processing event: {e}")
                        logger.error(f"Error processing event: {e}")
                        
            except Exception as e:
                EventMetrics.handle_error(f"Connection error: {e}")
                logger.error(f"Connection error: {e}")
                logger.info("Attempting to reconnect in 10 seconds...")
                time.sleep(10)
                vk_session = vk_api.VkApi(token = token['vk'])
                vk = vk_session.get_api()
                longpoll = VkBotLongPoll(vk_session, chat_id['vk'])
                
    except Exception as e:
        EventMetrics.handle_error(f"Fatal error in main loop: {e}")
        logger.critical(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    EventMetrics.start_metrics()
    main()