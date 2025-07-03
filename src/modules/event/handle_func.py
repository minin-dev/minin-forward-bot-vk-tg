# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import requests, json, vk_api, logging
from src.config.config import token, chat_id
from src.console.console_messages import send_message
from src.modules.metrics import EventMetrics

telegram_bot_token = token['tg']
telegram_chat_id = chat_id['tg']

vk_session = vk_api.VkApi(token = token['vk'])
vk = vk_session.get_api()

logger = logging.getLogger(__name__)

processed_messages = set()

@EventMetrics.histogram_timer()
def handle_text(user, text, mode=None):
    try:
        if mode == None:
            response = requests.post(
                        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                        data={
                             "chat_id": telegram_chat_id,
                             "text": f"<code>{user}</code>\n\n<strong><pre>{text}</pre></strong>",
                             "parse_mode": "HTML"
                             },
                        timeout=10)
            send_message("HANDLE_TEXT_RESPONSE_MODE=NONE", response.json())
            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
            else:
                EventMetrics.handle_error(f"Failed to send message: {response.status_code} - {response.text}")
        else:
            response = requests.post(
                        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                        data={
                             "chat_id": telegram_chat_id,
                             "text": f"{text}",
                             "parse_mode": "HTML"
                             },
                        timeout=10)
            send_message("HANDLE_TEXT_RESPONSE_MOD!=NONE", response.json())
            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
            else:
                EventMetrics.handle_error(f"Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        EventMetrics.handle_error(f"handle_text error: {e}")
        logger.error(f"Error in handle_text: {e}")

@EventMetrics.histogram_timer()
def get_user_name(message):
    message_author_info = vk.users.get(user_ids=message['from_id'])
    return f"{message_author_info[0]['first_name']} {message_author_info[0]['last_name']}"

@EventMetrics.histogram_timer()
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
        if response.status_code == 200:
            EventMetrics.TG_MESSAGES_SENT.inc()
            EventMetrics.ATTACHMENTS.labels('PHOTO').inc()
        else:
            EventMetrics.handle_error(f"Failed to send media group: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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

            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
                EventMetrics.ATTACHMENTS.labels('VIDEO').inc()
            else:
                EventMetrics.handle_error(f"Failed to send video message: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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

            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
                EventMetrics.ATTACHMENTS.labels('AUDIO_MESSAGE').inc()
            else:
                EventMetrics.handle_error(f"Failed to send audio message: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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
            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
                EventMetrics.ATTACHMENTS.labels('AUDIO').inc()
            else:
                EventMetrics.handle_error(f"Failed to send audio: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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
            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
                EventMetrics.ATTACHMENTS.labels('DOC').inc()
            else:
                EventMetrics.handle_error(f"Failed to send document message: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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

                    if response.status_code == 200:
                        EventMetrics.TG_MESSAGES_SENT.inc()
                        EventMetrics.ATTACHMENTS.labels('STICKER').inc()
                    else:
                        EventMetrics.handle_error(f"Failed to send sticker: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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

            if response.status_code == 200:
                EventMetrics.TG_MESSAGES_SENT.inc()
                EventMetrics.ATTACHMENTS.labels('POLL').inc()
            else:
                EventMetrics.handle_error(f"Failed to send poll message: {response.status_code} - {response.text}")

@EventMetrics.histogram_timer()
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
            EventMetrics.ATTACHMENTS.labels('WALL').inc()

@EventMetrics.histogram_timer()
def handle_link(message):
    try:
        message_id = f"link_{message.get('date', '')}_{message.get('conversation_message_id', '')}"
        
        if message_id in processed_messages:
            logger.info(f"Skipping already processed link: {message_id}")
            return
            
        processed_messages.add(message_id)
        
        attachments = message.get('attachments', [])
        for attachment in attachments:
            if attachment['type'] == 'link':
                link = attachment['link']
                title = link.get('title', 'Ссылка')
                url = link.get('url', '')
                description = link.get('description', '')
                
                link_text = f"<b>{title}</b>\n{description}\n\n<a href='{url}'>{url}</a>"
                
                response = requests.post(
                    f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                    data={
                        "chat_id": telegram_chat_id,
                        "text": link_text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": False
                    },
                    timeout=10
                )
                send_message("HANDLE_LINK_RESPONSE", response.json())
                if response.status_code == 200:
                    EventMetrics.TG_MESSAGES_SENT.inc()
                    EventMetrics.ATTACHMENTS.labels('LINK').inc()
                else:
                    EventMetrics.handle_error(f"Failed to send link message: {response.status_code} - {response.text}")
    except Exception as e:
        EventMetrics.handle_error(f"handle_link error: {e}")
        logger.error(f"Error in handle_link: {e}")

@EventMetrics.histogram_timer()
def handler(message, skip_reply=False):

    try:
        handle_photo(message)
        handle_video(message)
        handle_audio_message(message)
        handle_audio(message)
        handle_doc(message)
        handle_sticker(message)
        handle_poll(message)
        handle_wall(message)
        handle_link(message)

        if not skip_reply:
            handle_reply(message)
    except Exception as e:
        EventMetrics.handle_error(f"handler error: {e}")
        logger.error(f"Error in main handler: {e}")

@EventMetrics.histogram_timer()
def handle_reply(message):
    try:
        if "fwd_messages" in message and message["fwd_messages"]:
            for fwd_message in message["fwd_messages"]:
                try:
                    fwd_id = f"fwd_{fwd_message.get('date', '')}_{fwd_message.get('conversation_message_id', '')}"

                    if fwd_id in processed_messages:
                        logger.info(f"Skipping already processed forward: {fwd_id}")
                        continue
                        
                    processed_messages.add(fwd_id)
                    
                    message_author_info = vk.users.get(user_ids=fwd_message['from_id'])
                    message_author = f"{message_author_info[0]['first_name']} {message_author_info[0]['last_name']}"

                    message_text = fwd_message.get('text', '')

                    response = requests.post(
                        f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage",
                        data={
                            "chat_id": telegram_chat_id,
                            "text": f"<code>Ссылка на сообщение от {message_author} ✉</code>\n\n<pre>{message_text}</pre>",
                            "parse_mode": "HTML"
                        },
                        timeout=10
                    )
                    
                    send_message("HANDLE_REPLY_RESPONSE", response.json())

                    if response.status_code == 200:
                        EventMetrics.TG_MESSAGES_SENT.inc()
                    else:
                        EventMetrics.handle_error(f"Failed to send forwarded message: {response.status_code} - {response.text}")

                    handler(fwd_message, skip_reply=True)

                    if "fwd_messages" in fwd_message and fwd_message["fwd_messages"]:
                        handle_reply(fwd_message)
                        
                except Exception as e:
                    EventMetrics.handle_error(f"Error processing forwarded message: {e}")
                    logger.error(f"Error processing forwarded message: {e}")
    except Exception as e:
        EventMetrics.handle_error(f"handle_reply error: {e}")
        logger.error(f"Error in handle_reply: {e}")

def clear_processed_messages_cache():
    global processed_messages
    processed_messages = set()
    logger.info("Cleared processed messages cache")