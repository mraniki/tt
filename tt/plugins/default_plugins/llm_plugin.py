"""
    llm plugin (chatGPT / llama)

"""
import os

import g4f


from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class LlmPlugin(BasePlugin):
    """ llm_plugin Plugin """
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        super().__init__()
        self.enabled = settings.llm_enabled
        if self.enabled:
            self.version = "🦾"
            self.help_message = settings.llm_commands
            # self.llm = Client(
            # model=Model.gpt_35_turbo,
            # provider=Provider.Aichat,)


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
        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_help: self.get_llm_help,
                settings.bot_command_info: self.get_llm_info,
                settings.bot_command_llm: lambda: self.get_llm_run(args),
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

    async def get_llm_help(self):
        """Help Message"""
        return f"{self.help_message}"

    async def get_llm_info(self):
        """info Message"""
        return self.version

    async def get_llm_run(self,llm_request="hello"):
        """ 
        Gets the llm prompts response
        """
        
        return g4f.ChatCompletion.create(
            model=g4f.Model.gpt_4, 
            messages=[{"role": "user", "content": llm_request}]
            )

        
