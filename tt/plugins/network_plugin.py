import socket
import ping3
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings


class NetworkPlugin(BasePlugin):
    name = "network_plugin"
    def __init__(self):
        try:
            if settings.network_enabled:
                logger.info("network_plugin initialized")
        except Exception as e:
            logger.warning("network_plugin init %s",e)

    async def start(self):
        """Starts the plugin"""
        pass

    async def stop(self):
        """Stops the plugin"""
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            await send_notification(message)
        except Exception as e:
            logger.warning("plugin send_notification %s",e)

    def should_handle(self, message):
        """Returns True if the plugin should handle incoming message"""
        return False

    async def handle_message(self, msg):
        """Handles incoming messages"""
        # if msg == f"{settings.bot_prefix}{settings.bot_command_help}":
        #     await self.send_notification("this is an example from the example_plugin")
        # elif msg == f"{settings.bot_prefix}{settings.plugin_menu}":
        #     plugin_menu_message = f"⚙️:\n{settings.bot_prefix}{settings.plugin_menu}"
        #     await self.send_notification(plugin_menu_message)

    # def get_host_ip() -> str:
    #     """Returns host IP """
    #     try:
    #         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         s.connect((settings.ping, 80))
    #         ip_address = s.getsockname()[0]
    #         s.close()
    #         return ip_address
    #     except Exception:
    #         pass

    # def get_ping(host: str = settings.ping) -> float:
    #     """Returns latency """
    #     response_time = ping3.ping(host, unit='ms')
    #     time.sleep(1)
    #     return round(response_time, 3)