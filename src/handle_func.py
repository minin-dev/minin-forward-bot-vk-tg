import requests, json, vk_api
from src.config import token, chat_id
from src.console_messages import send_message

telegram_bot_token = token['tg']
telegram_chat_id = chat_id['tg']

vk_session = vk_api.VkApi(token = token['vk'])
vk = vk_session.get_api()

def handle_text(user, text, mode=None):
            if mode == None:
                response = requests.post(
                            f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                            data={
                                 "chat_id": telegram_chat_id,
                                 "text": f"<code>{user}</code>\n\n<strong><pre>{text}</pre></strong>",
                                 "parse_mode": "HTML"
                                 })
                send_message("HANDLE_TEXT_RESPONSE_MODE=NONE", response.json())
            else:
                response = requests.post(
                            f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                            data={
                                 "chat_id": telegram_chat_id,
                                 "text": f"{text}",
                                 "parse_mode": "HTML"
                                 })
                send_message("HANDLE_TEXT_RESPONSE_MOD!=NONE", response.json())

def get_user_name(message):
    message_author_info = vk.users.get(user_ids=message['from_id'])
    return f"{message_author_info[0]['first_name']} {message_author_info[0]['last_name']}"

def handle_photo(message):
    attachments = message['attachments']
    media_group = []
    for attachment in attachments:
        if attachment['type'] == 'photo':
            image = {"type": "photo", "media": f"{attachment['photo']['orig_photo']['url']}"}
            media_group.append(image)
    if media_group != []:
        media_group[0]["caption"] = f"<code>{get_user_name(message)} ✉</code>\n\n<pre>{message['text']}</pre>"
        media_group[0]["parse_mode"] = "HTML"
        response = requests.post(
            f"https://api.telegram.org/bot{telegram_bot_token}/sendMediaGroup",
            data={
                 'chat_id': telegram_chat_id,
                 'media': json.dumps(media_group)
                 })
        send_message("HANDLE_PHOTO_RESPONSE", response.json())

def handle_video(message):
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'video':
            title = attachment['video']['title']
            response = requests.post(
               f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
               data={
                    "chat_id": telegram_chat_id,
                    "text": f"<a href='https://vk.com/video{attachment['video']['owner_id']}_{attachment['video']['id']}'><code>Видеозапись: {title}</code></a>",
                    "parse_mode": "HTML"
                    })
            send_message("HANDLE_VIDEO_RESPONSE", response.json())

def handle_audio_message(message):
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'audio_message':
            audio_message = attachment['audio_message']
            audio_url = audio_message['link_mp3']
            audio_data = requests.get(audio_url).content
            response = requests.post(
                f"https://api.telegram.org/bot{telegram_bot_token}/sendVoice",
                files={"voice": audio_data},
                data={"chat_id": telegram_chat_id})
            send_message("HANDLE_AUDIO_MESSAGE_RESPONSE", response.json())
            
def handle_audio(message):
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'audio':
            audio_file = requests.get(attachment['audio']['url'])
            with open('other_files/audio.mp3', 'wb') as f:
                f.write(audio_file.content)
            with open('other_files/audio.mp3', 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'chat_id': telegram_chat_id, 'title': attachment['audio']['title'], 'performer': attachment['audio']['artist']}
                response = requests.post(f'https://api.telegram.org/bot{telegram_bot_token}/sendAudio', files=files, data=data)
            send_message("HANDLE_AUDIO_RESPONSE", response.json())

def handle_doc(message):
    attachments = message['attachments']
    for attachment in attachments:
         if attachment['type'] == 'doc':
            doc_url = attachment['doc']['url']
            doc_title = attachment['doc']['title']
            response = requests.post(
               f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
               data={
                    "chat_id": telegram_chat_id,
                    "text": f"<a href='{doc_url}'>{doc_title}</a>",
                    "parse_mode": "HTML"
                    })
            send_message("HANDLE_DOC_RESPONSE", response.json())

def handle_sticker(message):
    message_author_info = vk.users.get(user_ids=message['from_id'])
    message_author = f"{message_author_info[0]['first_name']} {message_author_info[0]['last_name']}"
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'sticker':
            for sticker_image in attachment['sticker']['images']:
                if sticker_image['width'] == 128 and sticker_image['height'] == 128:
                    image = {"type": "photo", "media": f"{sticker_image['url']}", "caption": f"{message_author} ✉"}
                    media_group = []
                    media_group.append(image)
                    response = requests.post(
                        f"https://api.telegram.org/bot{telegram_bot_token}/sendMediaGroup",
                        data={
                             "chat_id": telegram_chat_id,
                             "media": json.dumps(media_group)
                             })
                    send_message("HANDLE_STICKER_RESPONSE", response.json())

def handle_poll(message):
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'poll':
            response = requests.post(
               f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
               data={
                    "chat_id": telegram_chat_id,
                    "text": f"<code>Опрос: {attachment['poll']['question']}</code>",
                    "parse_mode": "HTML"
                    })
            send_message("HANDLE_POLL_RESPONSE", response.json())

def handle_wall(message):
    attachments = message['attachments']
    for attachment in attachments:
        if attachment['type'] == 'wall':
            if "text" in attachment['wall'] and attachment['wall']["text"] != "":
                post_id = {True: str(attachment['wall']['from_id'])[1:], False: attachment['wall']['from_id']}[str(attachment['wall']['from_id']).startswith('-')]
                group_of_wall = vk.groups.getById(group_id=post_id)
                group_name = group_of_wall[0]['name']
                handle_text(group_name+" ☆", attachment['wall']["text"])
                handle_text(None, f"\n\n<b><a href='https://vk.com/wall-{post_id}_{attachment['wall']['id']}'>✘ ДЛЯ ПРОСМОТРА ВСЕЙ ЗАПИСИ, НАЖМИТИ СЮДА!</a></b>", 1)
            else:
                handle_text(group_name+" ☆", "")


def handler(message):
    handle_photo(message)
    handle_video(message)
    handle_audio_message(message)
    handle_audio(message)
    handle_doc(message)
    handle_sticker(message)
    handle_poll(message)
    handle_wall(message)
    handle_reply(message)

def handle_reply(message):
    if "fwd_messages" in message:
        for fwd_message in message["fwd_messages"]:
            message_author_info = vk.users.get(user_ids=fwd_message['from_id'])
            message_author = f"{message_author_info[0]['first_name']} {message_author_info[0]['last_name']}"
            check_attacment = False
            for re_message in message["fwd_messages"]:
                for attachment in re_message["attachments"]:
                    if "photo" in attachment:
                        check_attacment = True
            if check_attacment == True:
                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                         "chat_id": telegram_chat_id,
                         "text": f"<code>Ссылка на сообщение от {message_author} ✉</code>",
                         "parse_mode": "HTML"
                         })
            else:
                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                         "chat_id": telegram_chat_id,
                         "text": f"<code>Ссылка на сообщение от {message_author} ✉</code>\n\n<pre>{fwd_message['text']}</pre>",
                         "parse_mode": "HTML"
                         })
            
            send_message("HANDLE_REPLY_RESPONSE", response.json())
            handler(fwd_message)