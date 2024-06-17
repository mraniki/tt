"""
    AI Agent plugin

"""

from myllm import MyLLM

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin


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
        self.ai_agent_mode = settings.ai_agent_mode or False
        self.ai_agent_prefix = settings.ai_agent_prefix or None
        if self.enabled:
            self.ai_agent = MyLLM()

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
        if self.should_filter(msg):
            # If the the message should not be handled, return
            return

        # If the message starts with the bot prefix,
        # it checks if it's the ai chat command.
        # If it is, it sends the result of the chat with the LLM.
        # If it's not, it checks if the command is in the command mapping
        # and sends the result of the corresponding function.
        # If it's not, it checks if the ai_agent setting is enabled
        # and sends the result of the chat with the LLM.
        if self.is_command_to_handle(msg):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.ai_agent.get_info,
                settings.bot_command_aiclear: self.ai_agent.clear_chat_history,
                settings.bot_command_aiexport: self.ai_agent.export_chat_history,
                settings.bot_command_aichat: lambda: self.ai_agent.chat(str(args)),
                settings.bot_command_aimode: self.ai_agent_switch_command,
            }
            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

        # If the ai_agent setting is enabled,
        # and the message does not start with ai_agent_prefix character
        # send the result of the chat with the LLM
        # bypassing the command mapping
        if settings.ai_agent_mode and not msg.startswith(self.ai_agent.ai_agent_prefix):
            await self.send_notification(f"{await self.ai_agent.chat(str(msg))}")

    async def ai_agent_switch_command(self) -> str:
        """
        AI Agent switch command
        :file:`/aimode` command
        to turn off or on the
        ai agent continuous capability
        """
        self.ai_agent_mode = not self.ai_agent_mode
        status = "enabled" if self.ai_agent_mode else "disabled"
        return f"AI Agent is {status}."
