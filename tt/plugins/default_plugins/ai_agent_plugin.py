"""
    AI Agent plugin

"""

from myllm import MyLLM

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class AIAgentPlugin(BasePlugin):
    """AI Agent Plugin"""

    def __init__(self):
        """
        Initializes the object.

        No parameters.

        No return value.
        """
        super().__init__()
        self.enabled = settings.myllm_enabled
        if self.enabled:
            self.ai_agent = MyLLM()

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """
        Handles incoming messages.

        If the message starts with the bot prefix,
        it checks if it's the ai chat command.
        If it is, it sends the result of the chat with the LLM.
        If it's not, it checks if the command is in the command mapping
        and sends the result of the corresponding function.
        If it's not, it checks if the ai_agent setting is enabled
        and sends the result of the chat with the LLM.

        Args:
            msg (str): The incoming message.

        Returns:
            None
        """
        if not self.should_handle(msg):
            # If the the message should not be handled, return
            return

        # If the message starts with the bot prefix,
        # it checks if it's the ai chat command.
        # If it is, it sends the result of the chat with the LLM.
        # If it's not, it checks if the command is in the command mapping
        # and sends the result of the corresponding function.
        # If it's not, it checks if the ai_agent setting is enabled
        # and sends the result of the chat with the LLM.
        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.ai_agent.get_info,
                settings.bot_command_aiclear: self.ai_agent.clear_chat_history,
                settings.bot_command_aiexport: self.ai_agent.export_chat_history,
                settings.bot_command_aichat: lambda: self.ai_agent.chat(str(args)),
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

        # If the ai_agent setting is enabled,
        # and the message does not start with a bot_ignore character
        # send the result of the chat with the LLM
        # bypassing the command mapping
        ignore_chars = list(settings.bot_ignore)
        if settings.ai_agent and not any(msg.startswith(char) for char in ignore_chars):
            await self.send_notification(f"{await self.ai_agent.chat(str(msg))}")
