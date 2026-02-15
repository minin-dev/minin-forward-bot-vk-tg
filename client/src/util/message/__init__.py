# Copyright (c) 2023 [Eiztrips]
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from .vk.processor import VkMessageProcessor
from .tg.processor import TgMessageProcessor

__all__ = ["VkMessageProcessor", "TgMessageProcessor"]
