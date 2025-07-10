# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
from dotenv import load_dotenv

load_dotenv()

token = {
    'vk': os.getenv('VK_TOKEN', ''),
    'tg': os.getenv('TG_BOT_TOKEN', '')
}


chat_id = {
    'vk': os.getenv('VK_CHAT_ID', ''),
    'tg': os.getenv('TG_CHAT_ID', '')
}

bd_dates = {
    '02-28': ['FirstName LastName', 'FirstName LastName'],
    '06-05': 'FirstName LastName',
    }

groq_api_key = os.getenv('GROQ_API_KEY', '')