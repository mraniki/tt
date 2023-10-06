"""
    llm plugin (chatGPT / llama)

"""
import os

from myllm import MyLLM

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class LlmPlugin(BasePlugin):
    """llm_plugin Plugin"""

    name = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        super().__init__()
        self.enabled = settings.myllm_enabled
        if self.enabled:
            self.llm = MyLLM()

    async def start(self):
        """Starts the plugin"""

    async def stop(self):
        """Stops the plugin"""

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if not self.should_handle(msg):
            return
        if self.llm.llm_ai_mode and not msg.startswith(settings.llm_prefix):
            await self.send_notification(f"{await self.llm.chat(str(msg))}")

        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.llm.get_myllm_info,
                settings.bot_command_aimode: self.llm.switch_continous_mode,
                settings.bot_command_aiclear: self.llm.clear_chat_history,
                settings.bot_command_aiexport: self.llm.export_chat_history,
                settings.bot_command_aichat: lambda: self.llm.chat(str(args)),
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")
