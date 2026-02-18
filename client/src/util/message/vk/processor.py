# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
from src.client.vk.client import VkClient
from src.client.tg.client import TgClient
from src.util.logger import Logger


class VkMessageProcessor:
    def __init__(self, tg_client: TgClient, vk_client: VkClient):
        self.tg_client = tg_client
        self.vk_client = vk_client
        self.logger = Logger()

    def process_message(self, message: dict) -> list:
        processed_messages = []
        raw_messages = [message] + self._extract_forwarded_messages(message, parent_id=message.get('from_id'))

        for raw_msg in raw_messages:
            text_processed = False
            from_id = raw_msg.get('from_id')
            is_forwarded = raw_msg.get('forwarded', False)
            text_content = raw_msg.get('text', '').strip()

            if 'attachments' in raw_msg:
                for attachment in raw_msg['attachments']:
                    attachment_type = attachment['type']

                    if attachment_type == 'photo':
                        self._process_photo(attachment, processed_messages, from_id, is_forwarded, text_content)
                        if not text_processed and text_content:
                            text_processed = True

                    elif attachment_type == 'video':
                        self._process_video(attachment, processed_messages, from_id, is_forwarded, text_content, text_processed)
                        if not text_processed and text_content:
                            text_processed = True

                    elif attachment_type == 'doc':
                        self._process_document(attachment, processed_messages, from_id, is_forwarded, text_content, text_processed)
                        if not text_processed and text_content:
                            text_processed = True

                    elif attachment_type == 'audio_message':
                        self._process_voice(attachment, processed_messages, from_id, is_forwarded)

                    elif attachment_type == 'audio':
                        self._process_audio(attachment, processed_messages, from_id, is_forwarded, text_content, text_processed)
                        if not text_processed and text_content:
                            text_processed = True

                    elif attachment_type == 'sticker':
                        self._process_sticker(attachment, processed_messages, from_id, is_forwarded)

                    elif attachment_type == 'wall':
                        self._process_wall(attachment, processed_messages, from_id, is_forwarded)

                    elif attachment_type == 'poll':
                        self._process_poll(attachment, processed_messages, from_id, is_forwarded)

            if text_content and not text_processed:
                processed_messages.append({
                    "type": "text",
                    "from_id": from_id,
                    "forwarded": is_forwarded,
                    "data": {"text": text_content}
                })

        return processed_messages

    def _extract_forwarded_messages(self, data: dict, parent_id=None) -> list:
        messages = []
        if 'fwd_messages' in data and data['fwd_messages']:
            for msg in data['fwd_messages']:
                msg['forwarded'] = True
                if 'from_id' not in msg and parent_id is not None:
                    msg['from_id'] = parent_id
                messages.append(msg)
                messages.extend(self._extract_forwarded_messages(msg, parent_id=msg.get('from_id', parent_id)))
        return messages

    def _process_photo(self, attachment, queue, from_id, forwarded, text):
        largest = max(attachment['photo']['sizes'], key=lambda x: x['height'] * x['width'])
        photo_url = largest['url']

        if queue and queue[-1]['type'] == 'photo_group':
            queue[-1]['data']['media'].append({"url": photo_url})
        else:
            queue.append({
                "type": "photo_group",
                "from_id": from_id,
                "forwarded": forwarded,
                "data": {
                    "media": [{"url": photo_url}],
                    "caption": text
                }
            })

    def _process_video(self, attachment, queue, from_id, forwarded, text, text_used):
        video = attachment['video']
        url = f"https://vk.com/video{video['owner_id']}_{video['id']}"
        if video.get('access_key'):
            url += f"?access_key={video['access_key']}"

        video_data = {"url": url, "title": video.get('title', '')}

        if queue and queue[-1]['type'] == 'video_group':
            queue[-1]['data']['media'].append(video_data)
        elif len(queue) >= 2 and queue[-2]['type'] == 'video_group':
             queue[-2]['data']['media'].append(video_data)
        else:
            caption = "" if text_used else text
            queue.append({
                "type": "video_group",
                "from_id": from_id,
                "forwarded": forwarded,
                "data": {
                    "media": [video_data],
                    "caption": caption
                }
            })

    def _process_document(self, attachment, queue, from_id, forwarded, text, text_used):
        doc = attachment['doc']
        url = doc['url']
        if doc.get('access_key'):
            url += doc['access_key']

        doc_data = {"url": url, "title": doc.get('title', '')}

        is_group = False
        target_idx = -1

        if queue:
            if queue[-1]['type'] == 'document_group':
                is_group = True
                target_idx = -1
            elif len(queue) >= 2 and queue[-2]['type'] == 'document_group':
                is_group = True
                target_idx = -2
            elif len(queue) >= 3 and queue[-3]['type'] == 'document_group':
                is_group = True
                target_idx = -3

        if is_group:
            queue[target_idx]['data']['documents'].append(doc_data)
        else:
            caption = "" if text_used else text
            queue.append({
                "type": "document_group",
                "from_id": from_id,
                "forwarded": forwarded,
                "data": {
                    "documents": [doc_data],
                    "caption": caption
                }
            })

    def _process_voice(self, attachment, queue, from_id, forwarded):
        audio = attachment['audio_message']
        queue.append({
            "type": "voice",
            "from_id": from_id,
            "forwarded": forwarded,
            "data": {
                "url": audio['link_ogg'],
                "duration": audio['duration']
            }
        })

    def _process_audio(self, attachment, queue, from_id, forwarded, text, text_used):
        audio = attachment['audio']
        caption = "" if text_used else text
        queue.append({
            "type": "audio",
            "from_id": from_id,
            "forwarded": forwarded,
            "data": {
                "url": audio['url'],
                "performer": audio.get('performer', ''),
                "title": audio.get('title', ''),
                "duration": audio.get('duration', 0),
                "caption": caption
            }
        })

    def _process_sticker(self, attachment, queue, from_id, forwarded):
        images = attachment['sticker']['images']
        index = len(images) // 4
        url = images[index]['url'] if images else ""

        queue.append({
            "type": "sticker",
            "from_id": from_id,
            "forwarded": forwarded,
            "data": {"url": url}
        })

    def _process_wall(self, attachment, queue, from_id, forwarded):
        wall = attachment['wall']
        url = f"https://vk.com/wall{wall['owner_id']}_{wall['id']}"
        queue.append({
            "type": "wall",
            "from_id": from_id,
            "forwarded": forwarded,
            "data": {"url": url}
        })

    def _process_poll(self, attachment, queue, from_id, forwarded):
        poll = attachment['poll']
        url = f"https://vk.com/poll{poll['owner_id']}_{poll['id']}"
        queue.append({
            "type": "poll",
            "from_id": from_id,
            "forwarded": forwarded,
            "data": {
                "url": url,
                "question": poll.get('question', '')
            }
        })
