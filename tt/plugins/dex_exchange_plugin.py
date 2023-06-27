import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
from dxsp import DexSwap
from findmyorder import FindMyOrder

class DexExchangePlugin(BasePlugin):
    """DEX Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        self.enabled = settings.dxsp_enabled
        if self.enabled:
            self.fmo = FindMyOrder()
            if settings.dex_chain_id:
                self.exchange = DexSwap()

    async def start(self):
        """Starts the exchange_plugin plugin"""


    async def stop(self):
        """Stops the exchange_plugin plugin"""


    async def send_notification(self, message):
        """Sends a notification"""
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
            trade = await self.execute_order(order)
            if trade:
                await send_notification(trade)
        if msg.startswith(settings.bot_prefix):
            command = (msg.split(" ")[0])[1:]
            if command == settings.bot_command_quote:
                symbol = msg.split(" ")[1]
                await self.send_notification(
                    f"{await self.exchange.get_quote(symbol)}")
            elif command == settings.bot_command_bal:
                await self.send_notification(f"{await self.get_account_balance()}")
            elif command == settings.bot_command_pos:
                await self.send_notification(f"{await self.get_account_position()}")
            elif command == settings.bot_command_help:
                await self.send_notification(await self.info_message())

    async def info_message(self):
        """info_message"""    
        exchange_name = await self.exchange.get_name()
        account_info = self.exchange.account
        return f"💱 {exchange_name}\n🪪 {account_info}"

    async def execute_order(self, order_params):
        """Execute order."""
        logger.debug("exchange plugin processing")
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        try:
            if not action or not instrument:
                return
            if isinstance(self.exchange, DexSwap):
                trade = await self.exchange.execute_order(order_params)
                return "⚠️ order execution failed" if not trade else trade
        except Exception as e:
            return f"⚠️ order execution: {e}"

    async def get_account_balance(self):
        """return account balance."""
        try:
            return "🏦 Balance\n" + str(await self.exchange.get_account_balance())
        except Exception as e:
            return f"⚠️ account_balance: {e}"

    async def get_account_position(self):
        """return account position."""
        try:
            if isinstance(self.exchange, DexSwap):
                open_positions = await self.exchange.get_account_position()
                position = "📊 Position\n" + str(open_positions)
                position += str(await self.exchange.get_account_margin())
                return position
        except Exception as e:
            return f"⚠️ account_position: {e}"


    async def get_trading_asset_balance(self):
        """return main asset balance."""
        return await self.exchange.get_trading_asset_balance()







