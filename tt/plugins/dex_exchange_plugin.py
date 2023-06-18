import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
from dxsp import DexSwap
from findmyorder import FindMyOrder

class DexExchangePlugin(BasePlugin):
    """DEX Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        try:
            self.enabled = settings.dxsp_enabled
            if self.enabled:
                self.fmo = FindMyOrder()
                if settings.dex_chain_id:
                    self.exchange = DexSwap()
                    print(self.exchange)
        except Exception as error:
            logger.warning(error)

    async def start(self):
        """Starts the exchange_plugin plugin"""
        try:
            pass
        except Exception as error:
            logger.warning(error)

    async def stop(self):
        """Stops the exchange_plugin plugin"""
        try:
            pass
        except Exception as error:
            logger.warning(error)

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            if self.enabled:
                await send_notification(message)
        except Exception as error:
            logger.warning(error)

    def should_handle(self, message):
        """Returns True if the plugin should handle the message"""
        return self.enabled

    async def handle_message(self, msg):
        """Handles incoming messages"""
        try:
            if self.enabled and await self.fmo.search(msg):
                order = await self.fmo.get_order(msg)
                trade = await self.execute_order(order)
                if trade:
                    await send_notification(trade)
            command = (msg.split(" ")[0])[1:]
            if command == settings.bot_command_quote:
                symbol = msg.split(" ")[1]
                await self.send_notification(f"{await self.exchange.get_quote(symbol)}")
            elif command == settings.bot_command_bal:
                await self.send_notification(f"{await self.get_account_balance()}")
            elif command == settings.bot_command_pos:
                await self.send_notification(f"{await self.get_account_position()}")
        except Exception as error:
            logger.warning(error)

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
                if not trade:
                    return "⚠️ order execution failed"

                trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
                trade_confirmation += trade['confirmation']

            return trade_confirmation

        except Exception as e:
            return f"⚠️ order execution: {e}"

    async def get_account_balance(self):
        """return account balance."""
        balance = "🏦 Balance\n"
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

    async def get_name(self):
        """Return exchange name"""
        try:
            return (await self.exchange.get_name())
        except Exception as e:
            return f"⚠️ exchange name: {e}"

    async def get_account(self):
        """Return exchange account"""
        try:
            return self.exchange.account

        except Exception as e:
            return f"⚠️ account: {e}"

    async def get_trading_asset_balance(self):
        """return main asset balance."""
        try:
            return await self.exchange.get_trading_asset_balance()
        except Exception as e:
            return f"⚠️ Check balance {settings.trading_asset}: {e}"






