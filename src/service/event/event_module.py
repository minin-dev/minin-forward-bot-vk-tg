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
from src.service.event.handle_func import handle_text, handler, clear_processed_messages_cache
from src.module.logs.logger import hello_message, event_message
from src.service.metrics import EventMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    try:
        vk_session = vk_api.VkApi(token=token['vk'])
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, "227054169")

        hello_message(datetime.datetime.now(), chat_id['tg'], chat_id['vk'])

        message_counter = 0

        while True:
            for event in longpoll.listen():
                try:
                    if event.type == VkBotEventType.MESSAGE_NEW and str(event.obj.message.get('peer_id')) == str(chat_id['vk']):
                        start = time.time()
                        EventMetrics.EVENT_COUNT.inc()
                        message_counter += 1

                        if message_counter >= 100:
                            clear_processed_messages_cache()
                            message_counter = 0

                        user_id = event.obj.message.get('from_id')
                        if not user_id:
                            continue
                        user_info = vk.users.get(user_ids=user_id)[0]
                        author = f"{user_info['first_name']} {user_info['last_name']}"

                        obj = vk.messages.getByConversationMessageId(
                            peer_id=event.obj['message']['peer_id'],
                            conversation_message_ids=event.obj['message']['conversation_message_id']
                        )['items'][0]

                        message_package = {
                            'author': author,
                            'object': obj
                        }

                        event_message(f"[HANDLE_EVENT_VK] {datetime.datetime.now()}", message_package['object'])

                        def main_forward(message):
                            if "text" in message and message["text"]:
                                has_photo = any(
                                    att.get("type") == "photo"
                                    for att in message.get("attachments", [])
                                )
                                if not has_photo:
                                    handle_text(message_package['author'] + " ✉", message["text"])
                            handler(message)

                        main_forward(message_package['object'])

                        elapsed = time.time() - start
                        fname = "main_forward"
                        if fname not in EventMetrics._timing_data:
                            EventMetrics._timing_data[fname] = [0.0, 0]
                        EventMetrics._timing_data[fname][0] += elapsed
                        EventMetrics._timing_data[fname][1] += 1
                        avg = EventMetrics._timing_data[fname][0] / EventMetrics._timing_data[fname][1]
                        EventMetrics.METHOD_PROCESSING_TIME.labels(method=fname).set(avg)

                except Exception as e:
                    EventMetrics.handle_error(f"Error processing event: {e}")
                    logger.error(f"Error processing event: {e}")

            # reconnect logic
            logger.info("Attempting to reconnect in 10 seconds...")
            time.sleep(10)
            vk_session = vk_api.VkApi(token=token['vk'])
            vk = vk_session.get_api()
            longpoll = VkBotLongPoll(vk_session, "227054169")

    except Exception as e:
        EventMetrics.handle_error(f"Fatal error in main loop: {e}")
        logger.critical(f"Fatal error: {e}")
        return 1

if __name__ == "__main__":
    EventMetrics.start_metrics()
    main()
