import src.config.config, src.modules.handle_func
import vk_api, datetime
from vk_api.bot_longpoll import VkBotLongPoll
from src.config.config import token, chat_id
from src.console.console_messages import hello_message, event_message

vk_session = vk_api.VkApi(token = token['vk'])
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, chat_id['vk'])

hello_message(datetime.datetime.now(), chat_id['tg'], chat_id['vk'])

for event in longpoll.listen():

    message_package = {
        'author': f"{vk.users.get(user_ids=event.obj.message['from_id'])[0]['first_name']} {vk.users.get(user_ids=event.obj.message['from_id'])[0]['last_name']}",
        'object': vk.messages.getByConversationMessageId(peer_id=event.obj['message']['peer_id'], conversation_message_ids=event.obj['message']['conversation_message_id'])['items'][0]
    }
    
    event_message(f"[HANDLE_EVENT_VK] {datetime.datetime.now()}", message_package['object'])

    def main_forward(message):
        if "text" in message and message["text"] != "": 
            check_attacment = False
            for attachment in message["attachments"]:
                if "photo" in attachment:
                    check_attacment = True
            if check_attacment == False: src.modules.handle_func.handle_text(message_package['author'] + " ✉", message["text"])
        src.modules.handle_func.handler(message)

    main_forward(message_package['object'])