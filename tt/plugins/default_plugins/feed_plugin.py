# from tt.config import logger, settings
# from tt.plugins.plugin_manager import BasePlugin
# from tt.utils import send_notification


# class FeedPlugin(BasePlugin):
#     """

#     """

#     def __init__(self):
#         """Plugin Initialization"""
#         super().__init__()
#         self.enabled = settings.example_plugin_enabled
#         if self.enabled:
#             logger.debug("example plugin enabled")

#     async def start(self):
#         """Starts the plugin"""
#         logger.debug("example plugin started")
#         if self.enabled:
#             logger.debug("example plugin enabled")

#     async def send_notification(self, message):
#         """Sends a notification"""
#         if self.enabled:
#             await send_notification(message)

#     async def handle_message(self, msg):
#         """
#         Handles incoming messages.

#         Args:
#             msg (str): The incoming message.
#         """
#         if not self.should_handle(msg):
#             return
