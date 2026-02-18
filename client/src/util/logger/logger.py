# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random
from typing import Any

class Logger:

    DEV_LOGO = """
██████╗░██╗███╗░░░███╗░░░░░░░░░░██████╗░███████╗
██╔══██╗██║████╗░████║░░░░░░░░░░╚════██╗██╔════╝
██████╔╝██║██╔████╔██║░░█████╗░░░░███╔═╝██████╗░
██╔═══╝░██║██║╚██╔╝██║░░╚════╝░░██╔══╝░░╚════██╗
██║░░░░░██║██║░╚═╝░██║░░░░░░░░░░███████╗██████╔╝
╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░░░░░░░░░╚══════╝╚═════╝░
    """
    SEPARATOR_CHARS = "☰☱☲☳☴☵☶☷"
    SEPARATOR_LENGTH = 55

    COLOR_RED = "\033[1;31m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[1;33m"
    COLOR_RESET = "\033[0m"

    def _generate_separator(self) -> str:
        return "".join(random.choice(self.SEPARATOR_CHARS) for _ in range(self.SEPARATOR_LENGTH))

    def start_message(self, time: str, tg_chat_id: int | str, vk_chat_id: int | str) -> None:
        separator = f"{self.COLOR_RED}{self._generate_separator()}{self.COLOR_RESET}"

        info_text = (
            f"{self.COLOR_GREEN} Hello, I'm bot for forwarding messages from VK to TG.\n"
            f" Developers: Eiztrips\n"
            f" Launch time: {time}\n"
            f" Telegram chat id: {tg_chat_id}\n"
            f" Vk chat id: {vk_chat_id} {self.COLOR_RESET}"
        )

        print(separator, flush=True)
        print(self.DEV_LOGO, flush=True)
        print(info_text, flush=True)
        print(separator, flush=True)

    def message(self, header: str, message: Any) -> None:
        print(f"\n{self.COLOR_YELLOW} {header} {self.COLOR_RESET}\n\n", message, flush=True)
