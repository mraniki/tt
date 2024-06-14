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
            self.llm = MyLLM()

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

        if msg.startswith(settings.bot_prefix):
            # Split the message into command and arguments
            command, *args = msg.split(" ", 1)
            command = command[1:]

            # If the command is the ai chat command,
            # send the chat result
            if command == settings.bot_command_aichat:
                result = await self.llm.chat(args[0] if args else "")
                await self.send_notification(f"{result}")
                return

            # If the command is in the command mapping,
            # send the result of the corresponding function
            command_mapping = {
                settings.bot_command_info: self.llm.get_info,
                settings.bot_command_aiclear: self.llm.clear_chat_history,
                settings.bot_command_aiexport: self.llm.export_chat_history,
            }

            if command in command_mapping:
                await self.send_notification(f"{await command_mapping[command]()}")

        # If the ai_agent setting is enabled,
        # send the result of the chat with the LLM
        if settings.ai_agent:
            await self.send_notification(f"{await self.llm.chat(str(msg))}")

