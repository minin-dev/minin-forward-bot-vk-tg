# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TG_BOT_TOKEN: str
    VK_BOT_TOKEN: str
    TG_CHAT_ID: str
    VK_CHAT_ID: str
    VK_GROUP_ID: str
    POLL_INTERVAL: int = 5

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")

settings = Settings(_env_file=env_path)