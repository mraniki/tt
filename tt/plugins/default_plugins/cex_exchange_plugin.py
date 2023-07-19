import os

import ccxt
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class CexExchangePlugin(BasePlugin):
    """CEX Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        self.enabled = settings.cex_enabled
        if self.enabled:
            self.fmo = FindMyOrder()
            self.exchange = CexExchange()

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
            if order and settings.trading_enabled:
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




class CexExchange():
    """CEX Object"""
    def __init__(self):
        if settings.cex_name:
            client = getattr(ccxt, settings.cex_name)
            self.cex = client({
                'apiKey': settings.cex_api,
                'secret': settings.cex_secret,
                'password': (settings.cex_password or ''),
                'enableRateLimit': True,
                'options': {
                    'defaultType': settings.cex_defaulttype,
                            }})
            if settings.cex_testmode:
                self.cex.set_sandbox_mode('enabled')
    async def get_info(self):
        """info_message"""    
        exchange_name = self.cex.id
        account_info = self.cex.uid
        return f"💱 {exchange_name}\n🪪 {account_info}"

    async def get_quote(self, symbol):
        """return main asset balance."""
        return f"🏦 {self.cex.fetchTicker(symbol).get('last')}"

    async def get_trading_asset_balance(self):
        """return main asset balance."""
        return self.cex.fetchBalance()[f"{settings.trading_asset}"]["free"]

    async def get_account_balance(self):
        """return account balance."""
        raw_balance = self.cex.fetch_free_balance()
        filtered_balance = {k: v for k, v in
                            raw_balance.items()
                            if v is not None and v > 0}
        balance = "🏦 Balance\n" + "".join(
            f"{iterator}: {value} \n"
            for iterator, value in filtered_balance.items()
        )
        if not balance:
            balance += "No Balance"
        return balance

    async def get_account_position(self):
        """return account position."""
        open_positions = self.cex.fetch_positions()
        open_positions = [p for p in open_positions if p['type'] == 'open']
        position = "📊 Position\n" + str(open_positions)
        position += str(await self.cex.fetch_balance({'type': 'margin',}))
        return position

    async def get_account_pnl(self):
        """return account pnl."""
        return 0

    async def execute_order(self, order_params):
        """Execute order."""
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', settings.trading_risk_amount)

        try:
            if not action or not instrument:
                return
            if await self.get_account_balance() == "No Balance":
                return "⚠️ Check Balance"

            asset_out_quote = float(
                self.cex.fetchTicker(f'{instrument}').get('last'))
            asset_out_balance = await self.get_trading_asset_balance()

            if not asset_out_balance:
                return

            transaction_amount = (
                asset_out_balance * (float(quantity) / 100) / asset_out_quote)

            trade = self.cex.create_order(
                instrument,
                settings.cex_ordertype,
                action,
                transaction_amount
            )

            if not trade:
                return

            trade_confirmation = (f"⬇️ {instrument}"
            if (action == "SELL") else f"⬆️ {instrument}\n")
            trade_confirmation += f"➕ Size: {round(trade['amount'], 4)}\n"
            trade_confirmation += f"⚫️ Entry: {round(trade['price'], 4)}\n"
            trade_confirmation += f"ℹ️ {trade['id']}\n"
            trade_confirmation += f"🗓️ {trade['datetime']}"

            return trade_confirmation

        except Exception as e:
            return f"⚠️ order execution: {e}"
