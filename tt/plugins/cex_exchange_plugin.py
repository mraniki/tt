import os
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings
import ccxt
from findmyorder import FindMyOrder

class CexExchangePlugin(BasePlugin):
    """CEX Plugin"""
    name = os.path.splitext(os.path.basename(__file__))[0]
    def __init__(self):
        try:
            self.enabled = settings.cex_enabled
            if self.enabled:
                logger.info("exchange_plugin: init")
                self.fmo = FindMyOrder()
                if settings.cex_name:
                    logger.info("WIP CEX SETUP")
                    client = getattr(ccxt, settings.cex_name)
                    self.exchange = client({
                        'apiKey': settings.cex_api,
                        'secret': settings.cex_secret,
                        'password': (settings.cex_password or ''),
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': settings.cex_defaulttype,
                                    }})
                    if settings.cex_testmode:
                        self.exchange.set_sandbox_mode('enabled')
                    print(self.exchange)
        except Exception as error:
            logger.warning(error)

    async def start(self):
        """Starts the exchange_plugin plugin"""
        try:
            if self.enabled:
                pass
        except Exception as error:
            logger.warning(error)

    async def stop(self):
        """Stops the exchange_plugin plugin"""
        try:
            if self.enabled:
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
                await send_notification(f"{await self.get_quote(symbol)}")
            elif command == settings.bot_command_bal:
                await send_notification(f"{await self.get_account_balance()}")
            elif command == settings.bot_command_pos:
                await send_notification(f"{await self.get_account_position()}")
        except Exception as error:
            logger.warning(error)

    async def execute_order(self, order_params):
        """Execute order."""
        logger.debug("exchange plugin processing")
        action = order_params.get('action')
        instrument = order_params.get('instrument')
        quantity = order_params.get('quantity', settings.trading_risk_amount)

        try:
            if not action or not instrument:
                return
            if await self.get_account_balance() == "No Balance":
                return "⚠️ Check Balance"

            asset_out_quote = float(self.exchange.fetchTicker(f'{instrument}').get('last'))
            asset_out_balance = await self.get_trading_asset_balance()

            if not asset_out_balance:
                return

            transaction_amount = (asset_out_balance * (float(quantity) / 100) / asset_out_quote)

            trade = self.exchange.create_order(
                instrument,
                settings.cex_ordertype,
                action,
                transaction_amount
            )

            if not trade:
                return

            trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
            trade_confirmation += f"➕ Size: {round(trade['amount'], 4)}\n"
            trade_confirmation += f"⚫️ Entry: {round(trade['price'], 4)}\n"
            trade_confirmation += f"ℹ️ {trade['id']}\n"
            trade_confirmation += f"🗓️ {trade['datetime']}"

            return trade_confirmation

        except Exception as e:
            return f"⚠️ order execution: {e}"

    async def get_account_balance(self):
        """return account balance."""
        balance = "🏦 Balance\n"
        try:
            raw_balance = self.exchange.fetch_free_balance()
            filtered_balance = {k: v for k, v in
                                raw_balance.items()
                                if v is not None and v > 0}
            balance += "".join(f"{iterator}: {value} \n" for
                            iterator, value in
                            filtered_balance.items())
            if not balance:
                balance += "No Balance"
            return balance
        except Exception as e:
            return f"⚠️ account_balance: {e}"

    async def get_quote(self, symbol):
        """return quote"""
        try:
            logger.debug("get_quote: %s", symbol)
            return f"🏦 {await self.exchange.fetchTicker (symbol)}"
        except Exception as e:
            return f"⚠️ quote: {e}"

    async def get_account_position(self):
        """return account position."""
        try:
            open_positions = self.exchange.fetch_positions()
            open_positions = [p for p in open_positions if p['type'] == 'open']
            position = "📊 Position\n" + str(open_positions)
            position += str(await self.get_account_margin())
            return position
        except Exception as e:
            return f"⚠️ account_position: {e}"

    async def get_account_margin(self):
        try:
            await self.exchange.fetch_balance({'type': 'margin',})
        except Exception as e:
            return f"⚠️ account_margin: {e}"

    async def get_name(self):
        """Return exchange name"""
        try:
            return  self.exchange.id
        except Exception as e:
            return f"⚠️ exchange name: {e}"

    async def get_trading_asset_balance(self):
        """return main asset balance."""
        try:
            return self.exchange.fetchBalance()[f"{settings.trading_asset}"]["free"]
        except Exception as e:
            return f"⚠️ Check balance {settings.trading_asset}: {e}"

    # async def get_account(exchange):
    #     """Return exchange account"""
    #     try:
    #         return (exchange.account
    #                 if isinstance(exchange, DexSwap)
    #                 else str(exchange.uid))
    #     except Exception as e:
    #         return f"⚠️ account: {e}"








