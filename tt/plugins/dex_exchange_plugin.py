import os
from tt.utils import BasePlugin, send_notification
from tt.config import settings
from dxsp import DexSwap
from findmyorder import FindMyOrder


class DexExchangePlugin(BasePlugin):
    """DEX Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        self.enabled = settings.dxsp_enabled
        if self.enabled:
            self.fmo = FindMyOrder()
            if settings.dex_wallet_address:
                self.exchange = DexSwap()

    async def start(self):
        """Starts the plugin"""

    async def stop(self):
        """Stops the plugin"""

    async def send_notification(self, message):
        """Sends notification"""
        if self.enabled:
            await send_notification(message)

    def should_handle(self, message):
        """Returns True if the plugin should handle the message"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        if not self.enabled:
            return

        if msg.startswith(settings.bot_ignore):
            return

        if await self.fmo.search(msg):
            order = await self.fmo.get_order(msg)
            if order:
                trade = await self.exchange.execute_order(order)
                if trade:
                    await send_notification(trade)

        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_help: self.exchange.get_info,
                settings.bot_command_quote: lambda: self.exchange.get_quote(args[0]),
                settings.bot_command_bal: self.exchange.get_account_balance,
                settings.bot_command_pos: self.exchange.get_account_position,
                settings.bot_command_pnl_daily: self.exchange.get_account_pnl,
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

