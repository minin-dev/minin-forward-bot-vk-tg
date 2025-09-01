# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random

class PIMLogger():

    dev_logo ="""
██████╗░██╗███╗░░░███╗░░░░░░░░░░██████╗░███████╗
██╔══██╗██║████╗░████║░░░░░░░░░░╚════██╗██╔════╝
██████╔╝██║██╔████╔██║░░█████╗░░░░███╔═╝██████╗░
██╔═══╝░██║██║╚██╔╝██║░░╚════╝░░██╔══╝░░╚════██╗
██║░░░░░██║██║░╚═╝░██║░░░░░░░░░░███████╗██████╔╝
╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░░░░░░░░░╚══════╝╚═════╝░
              """

    def terminal_cap_generator(self):
        cap = ""
        for i in range(55):
            cap += "☰☱☲☳☴☵☶☷"[random.randint(0, len("☰☱☲☳☴☵☶☷")-1)]
        return cap

    def start_message(self, time, tg_chat_id, vk_chat_id):
        print("\033[1;31m" + self.terminal_cap_generator() + "\033[0m", flush=True)
        print(self.dev_logo, flush=True)
        print(f"\033[32m Hello, I'm bot for forwarding messages from VK to TG.\n Developers: Eiztrips\n Launch time: {time}\n Telegram chat id: {tg_chat_id}\n Vk chat id: {vk_chat_id} \033[0m", flush=True)
        print("\033[1;31m" + self.terminal_cap_generator() + "\033[0m", flush=True)

    def message(self, header, message):
        print(f"\n\033[1;33m {header} \033[0m\n\n", message, flush=True)
