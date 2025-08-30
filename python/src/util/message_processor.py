class VkMessageProcessor:
    def process_message(self, message: dict) -> list:
        MessageQueue, VkMessageQueue = [], [message] + self.get_forwarded_messages(message)

        for data in VkMessageQueue:
            text_has_been_used = False
            if 'attachments' in data:
                for attachment in data['attachments']:
                    if attachment['type'] == 'photo':
                        largest_photo = max(attachment['photo']['sizes'], key=lambda x: x['height'] * x['width'])
                        if MessageQueue[-1:] and MessageQueue[-1]['type'] == 'media_group':
                            MessageQueue[-1]['media'].append({"type": "photo", "url":largest_photo['url']})
                        else:
                            MessageQueue.append({
                                "type": "media_group",
                                "from_id": data.get('from_id', None),
                                "media": [{"type": "photo", "url":largest_photo['url']}],
                                "caption": data.get('text', '').strip(),
                            })
                            text_has_been_used = True
                    elif attachment['type'] == 'video':
                        video_id = attachment['video']['id']
                        owner_id = attachment['video']['owner_id']
                        access_key = attachment['video'].get('access_key', '')
                        video_url = f"https://vk.com/video{owner_id}_{video_id}"
                        if access_key:
                            video_url += f"?access_key={access_key}"
                        if MessageQueue[-1:] and MessageQueue[-1]['type'] == 'media_group':
                            MessageQueue[-1]['media'].append({"type": "video", "url": video_url})
                        else:
                            MessageQueue.append({
                                "type": "media_group",
                                "from_id": data.get('from_id', None),
                                "media": [{"type": "video", "url": video_url}],
                                "caption": data.get('text', '').strip()
                            })
                            text_has_been_used = True
                    elif attachment['type'] == 'audio_message':
                        audio_url = attachment['audio_message']['link_ogg']
                        duration = attachment['audio_message']['duration']
                        MessageQueue.append({
                            "type": "voice",
                            "from_id": data.get('from_id', None),
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
                        MessageQueue.append({
                            "type": "audio",
                            "from_id": data.get('from_id', None),
                            "data": {
                                "url": audio_url,
                                "performer": performer,
                                "title": title,
                                "duration": duration,
                                "caption": data.get('text', '').strip() if not text_has_been_used else ""
                            }
                        })
                    elif attachment['type'] == 'doc':
                        doc_url = attachment['doc']['url']
                        MessageQueue.append({
                            "type": "document",
                            "from_id": data.get('from_id', None),
                            "data": doc_url,
                            "caption": data.get('text', '').strip() if not text_has_been_used else ""
                        })
                    elif attachment['type'] == 'sticker':
                        sticker_url = attachment['sticker']['images'][-1]['url']
                        MessageQueue.append({
                            "type": "sticker",
                            "from_id": data.get('from_id', None),
                            "data": sticker_url
                        })
                    elif attachment['type'] == 'wall':
                        wall_id = attachment['wall']['id']
                        owner_id = attachment['wall']['owner_id']
                        wall_url = f"https://vk.com/wall{owner_id}_{wall_id}"
                        MessageQueue.append({
                            "type": "wall",
                            "from_id": data.get('from_id', None),
                            "data": wall_url
                        })
            if 'text' in data and data['text'].strip():
                if not(text_has_been_used):
                    MessageQueue.append({
                        "type": "text",
                        "from_id": data.get('from_id', None),
                        "data": data['text'].strip()
                    })

        return MessageQueue

    def get_forwarded_messages(self, data: dict) -> list:
        messages = []
        if 'fwd_messages' in data and data['fwd_messages']:
            for msg in data['fwd_messages']:
                messages.append(msg)
                messages.extend(self.get_forwarded_messages(msg))
        return messages