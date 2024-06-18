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
        Initializes an instance of the AIAgentPlugin class.

        This method initializes the instance
        by calling the parent class's constructor
        using the `super()` function.
        It also sets the `enabled` attribute
        based on the value of the
        `myllm_enabled` setting in the `settings` module.
        The `ai_agent_mode` attribute is set to
        the value of the `ai_agent_mode` setting,
        or `False` if it is not set.
        The `ai_agent_prefix` attribute is set to
        the value of the `ai_agent_prefix` setting,
        or `None` if it is not set.
        If `enabled` is `True`, a new instance of
        the `MyLLM` class is created and assigned
        to the `ai_agent` attribute.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.enabled = settings.myllm_enabled
        self.ai_agent_mode = settings.ai_agent_mode or False
        self.ai_agent_prefix = settings.ai_agent_prefix or None
        if self.enabled:
            self.ai_agent = MyLLM()

    async def handle_message(self, msg):
        """
        Handles incoming messages and
        routes them to the appropriate function.

        Args:
            msg (str): The message received by the plugin.

        Supported functions are:

        - `get_info()`
        - `clear_chat_history()`
        - `export_chat_history()`
        - `chat()`
        - `ai_agent_switch_command()`

        """
        if self.should_filter(msg):
            return

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

        if settings.ai_agent_mode:  # and not msg.startswith(self.ai_agent_prefix):
            await self.send_notification(f"{await self.ai_agent.chat(str(msg))}")

    async def ai_agent_switch_command(self) -> str:
        """
        AI Agent switch command
        :file:`/aimode` command
        or your own defined command
        to turn off or on the
        ai agent continuous capability
        """
        self.ai_agent_mode = not self.ai_agent_mode
        status = "enabled" if self.ai_agent_mode else "disabled"
        return f"AI Agent is {status}."
