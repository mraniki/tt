"""
 talky Plugins Message_Processor
"""

from tt.config import logger

class MessageProcessor:
    """👂 Message Processor for plugin """
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def load_plugins(self):
        """ Load plugins using the plugin manager """
        self.plugin_manager.load_plugins()
        self.plugins = self.plugin_manager.plugins

    async def start_all_plugins(self):
        """ Start all plugins """
        try:
            for plugin in self.plugins:
                await plugin.start()
        except Exception as error:
            logger.error("Error starting plugins: %s", error)

    async def process_message(self, message):
        """ Process message from the plugin """
        for plugin in self.plugins:
            if plugin.should_handle(message):
                await plugin.handle_message(message)
