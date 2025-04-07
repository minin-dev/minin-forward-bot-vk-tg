# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random

dev_logo = """
█▀▀ █ ▀█ ▀█▀ █▀█ █ █▀█ █▀ ▄▄ █▀▄ █▀▀ █░█
██▄ █ █▄ ░█░ █▀▄ █ █▀▀ ▄█ ░░ █▄▀ ██▄ ▀▄▀
"""

def terminal_cap_generator():
    cap = ""
    for i in range(55):
        cap += "☰☱☲☳☴☵☶☷"[random.randint(0, len("☰☱☲☳☴☵☶☷")-1)]
    return cap

def hello_message(time, tg_chat_id, vk_chat_id):
    print("\033[1;31m" + terminal_cap_generator() + "\033[0m")
    print(dev_logo)
    print(f"\033[32m Hello, I'm bot for forwarding messages from VK to TG.\n Developers: Eiztrips\n Launch time: {time}\n Telegram chat id: {tg_chat_id}\n Vk chat id: {vk_chat_id} \033[0m")
    print("\033[1;31m" + terminal_cap_generator() + "\033[0m")

def event_message(header, message):
    print(f"\n\033[1;33m {header} \033[0m\n\n", message)

def send_message(header, message):
    print(f"\n\033[1;32m {header} \033[0m\n\n", message)