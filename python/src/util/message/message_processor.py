# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

class VkMessageProcessor:
    def process_message(self, message: dict) -> list:
        MessageQueue, VkMessageQueue = ([{'type': 'text_position'}],
                                        [message] + self.get_forwarded_messages(message, parent_from_id=message.get('from_id')))
        for data in VkMessageQueue:
            text_has_been_used = False
            if 'attachments' in data:
                for attachment in data['attachments']:
                    if attachment['type'] == 'photo':
                        largest_photo = max(attachment['photo']['sizes'], key=lambda x: x['height'] * x['width'])
                        if MessageQueue[-1:] and MessageQueue[-1]['type'] == 'photo_group':
                            MessageQueue[-1]['data']['media'].append({"url":largest_photo['url']})
                        else:
                            MessageQueue.append({
                                "type": "photo_group",
                                "from_id": data.get('from_id', None),
                                "forwarded": data.get('forwarded', False),
                                "data": {
                                    "media": [{"url": largest_photo['url']}],
                                    "caption": data.get('text', '').strip(),
                                }
                            })
                            text_has_been_used = True
                    elif attachment['type'] == 'video':
                        video_id = attachment['video']['id']
                        owner_id = attachment['video']['owner_id']
                        access_key = attachment['video'].get('access_key', '')
                        video_url = f"https://vk.com/video{owner_id}_{video_id}"
                        if access_key:
                            video_url += f"?access_key={access_key}"
                        if MessageQueue[-1:] and MessageQueue[-1]['type'] == 'video_group'\
                                or (len(MessageQueue) >= 2 and MessageQueue[-2]['type'] == 'video_group'):
                            MessageQueue[-1]['data']['media'].append({"url": video_url, "title": attachment['video'].get('title', '')})
                        else:
                            caption = ("" if text_has_been_used else data.get('text', '').strip())
                            MessageQueue.append({
                                "type": "video_group",
                                "from_id": data.get('from_id', None),
                                "forwarded": data.get('forwarded', False),
                                "data": {
                                    "media": [{"url": video_url, "title": attachment['video'].get('title', '')}],
                                    "caption": caption
                                }
                            })
                            text_has_been_used = True
                    elif attachment['type'] == 'doc':
                        doc_url = attachment['doc']['url'] + attachment['doc'].get('access_key', '')
                        caption = ""
                        title = attachment['doc'].get('title', '')
                        if (MessageQueue[-1:] and (MessageQueue[-1]['type'] == 'document_group')
                                or (len(MessageQueue) >= 2 and MessageQueue[-2]['type'] == 'document_group'))\
                                or (len(MessageQueue) >= 3 and MessageQueue[-3]['type'] == 'document_group'):
                            MessageQueue[-1 if MessageQueue[-1]['type'] == 'document_group' else -2]['data']['documents'].append({"url": doc_url, "title": title})
                        else:
                            if not(text_has_been_used):
                                caption = data.get('text', '').strip()
                                text_has_been_used = True
                            MessageQueue.append({
                                "type": "document_group",
                                "from_id": data.get('from_id', None),
                                "forwarded": data.get('forwarded', False),
                                "data": {
                                    "documents": [{"url": doc_url, "title": title}],
                                    "caption": caption
                                }
                            })
                    elif attachment['type'] == 'audio_message':
                        audio_url = attachment['audio_message']['link_ogg']
                        duration = attachment['audio_message']['duration']
                        MessageQueue.append({
                            "type": "voice",
                            "from_id": data.get('from_id', None),
                            "forwarded": data.get('forwarded', False),
                            "data": {
                                "url": audio_url,
                                "duration": duration
                            }
                        })
                    elif attachment['type'] == 'audio':
                        audio_url = attachment['audio']['url']
                        performer = attachment['audio'].get('performer', '')
                        title = attachment['audio'].get('title', '')
                        duration = attachment['audio'].get('duration', 0)
                        caption = ""
                        if not(text_has_been_used):
                            caption = data.get('text', '').strip()
                            text_has_been_used = True
                        MessageQueue.append({
                            "type": "audio",
                            "from_id": data.get('from_id'),
                            "forwarded": data.get('forwarded', False),
                            "data": {
                                "url": audio_url,
                                "performer": performer,
                                "title": title,
                                "duration": duration,
                                "caption": caption
                            }
                        })
                    elif attachment['type'] == 'sticker':
                        sticker_url = attachment['sticker']['images'][len(attachment['sticker']['images'])//4]['url']
                        MessageQueue.append({
                            "type": "sticker",
                            "from_id": data.get('from_id', None),
                            "forwarded": data.get('forwarded', False),
                            "data": {
                                "url": sticker_url
                            }
                        })
                    elif attachment['type'] == 'wall':
                        wall_id = attachment['wall']['id']
                        owner_id = attachment['wall']['owner_id']
                        wall_url = f"https://vk.com/wall{owner_id}_{wall_id}"
                        MessageQueue.append({
                            "type": "wall",
                            "from_id": data.get('from_id', None),
                            "forwarded": data.get('forwarded', False),
                            "data": {"url": wall_url}
                        })
                    elif attachment['type'] == 'poll':
                        poll_id = attachment['poll']['id']
                        owner_id = attachment['poll']['owner_id']
                        poll_url = f"https://vk.com/poll{owner_id}_{poll_id}"
                        MessageQueue.append({
                            "type": "poll",
                            "from_id": data.get('from_id', None),
                            "forwarded": data.get('forwarded', False),
                            "data": {"url": poll_url, "question": attachment['poll'].get('question', '')}
                        })
            if 'text' in data and data['text'].strip():
                if not text_has_been_used:
                    MessageQueue.append({
                        "type": "text",
                        "from_id": data.get('from_id', None),
                        "forwarded": data.get('forwarded', False),
                        "data": {
                            "text": data['text'].strip()
                        }
                    })

        return MessageQueue

    def get_forwarded_messages(self, data: dict, parent_from_id=None) -> list:
        messages = []
        if 'fwd_messages' in data and data['fwd_messages']:
            for msg in data['fwd_messages']:
                msg['forwarded'] = True
                if 'from_id' not in msg and parent_from_id is not None:
                    msg['from_id'] = parent_from_id
                messages.append(msg)
                messages.extend(self.get_forwarded_messages(msg, parent_from_id=msg.get('from_id', parent_from_id)))
        return messages