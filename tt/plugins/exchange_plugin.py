import ccxt
from dxsp import DexSwap
from tt.utils import BasePlugin, send_notification
from tt.config import logger, settings

class ExchangePlugin(BasePlugin):
    name = "exchange_plugin"
    def __init__(self):
        try:
            if settings.exchange_enabled:
                logger.info("exchange_plugin: init")
                if settings.cex_name:
                    logger.info("WIP CEX SETUP")
                #     client = getattr(ccxt, settings.cex_name)
                #     self.exchange = client({
                #         'apiKey': settings.cex_api,
                #         'secret': settings.cex_secret,
                #         'password': (settings.cex_password or ''),
                #         'enableRateLimit': True,
                #         'options': {
                #             'defaultType': settings.cex_defaulttype,
                #                     }})
                #     if settings.cex_testmode:
                #         self.exchange.set_sandbox_mode('enabled')
                elif settings.dex_chain_id:
                    logger.info("WIP DEX SETUP")
                #     self.exchange = DexSwap()
        except Exception as e:
            logger.warning("exchange: %s", e)

    async def start(self):
        """Starts the exchange_plugin plugin"""
        try:           
            pass
        except Exception as e:
            logger.warning("exchange_plugin start %s",e)

    async def stop(self):
        """Stops the exchange_plugin plugin"""
        pass

    async def send_notification(self, message):
        """Sends a notification"""
        try:
            await send_notification(message)
        except Exception as e:
            logger.warning("exchange_plugin send_notification %s",e)

    def should_handle(self, message):
        """Returns True if the plugin should handle the message"""
        return False

    async def handle_message(self, msg):
        """Handles incoming messages"""
        # if settings.trading_enabled and await fmo.search(msg):
        #     # Order parsing
        #     order = await fmo.get_order(msg)
        #     # Order execution
        #     order = await execute_order(order)
        #     if order:
        #         await send_notification(order)
    #     elif command == settings.bot_command_quote:
            # symbol = msg.split(" ")[1]
            # message = await get_quote(symbol)
        # elif command == settings.bot_command_bal:
        #     await account_balance_command()
        # elif command == settings.bot_command_pos:
        #     message = await account_position_command()

    # async def execute_order(order_params):
    #     """Execute order."""

    #     action = order_params.get('action')
    #     instrument = order_params.get('instrument')
    #     quantity = order_params.get('quantity', settings.trading_risk_amount)

    #     try:
    #         if not action or not instrument:
    #             return

    #         if isinstance(exchange, DexSwap):
    #             trade = await exchange.execute_order(order_params)
    #             if not trade:
    #                 return "⚠️ order execution failed"

    #             trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
    #             trade_confirmation += trade['confirmation']

    #         else:
    #             if await get_account_balance() == "No Balance":
    #                 return "⚠️ Check Balance"

    #             asset_out_quote = float(exchange.fetchTicker(f'{instrument}').get('last'))
    #             asset_out_balance = await get_trading_asset_balance()

    #             if not asset_out_balance:
    #                 return

    #             transaction_amount = (asset_out_balance * (float(quantity) / 100) / asset_out_quote)

    #             trade = exchange.create_order(
    #                 instrument,
    #                 settings.cex_ordertype,
    #                 action,
    #                 transaction_amount
    #             )

    #             if not trade:
    #                 return

    #             trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
    #             trade_confirmation += f"➕ Size: {round(trade['amount'], 4)}\n"
    #             trade_confirmation += f"⚫️ Entry: {round(trade['price'], 4)}\n"
    #             trade_confirmation += f"ℹ️ {trade['id']}\n"
    #             trade_confirmation += f"🗓️ {trade['datetime']}"

    #         return trade_confirmation

    #     except Exception as e:
    #         return f"⚠️ order execution: {e}"
        

    # async def get_quote(symbol):
    #     """return quote"""
    #     try:
    #         logger.debug("get_quote: %s", symbol)
    #         if isinstance(exchange, DexSwap):
    #             return (await exchange.get_quote(symbol))
    #         else:
    #             return f"🏦 {await exchange.fetchTicker (symbol)}"
    #     except Exception as e:
    #         return f"⚠️ quote: {e}"


    # async def get_name():
    #     """Return exchange name"""
    #     try:
    #         return (
    #             await exchange.get_name()
    #             if isinstance(exchange, DexSwap)
    #             else exchange.id)
    #     except Exception as e:
    #         return f"⚠️ exchange name: {e}"


    # async def get_account(exchange):
    #     """Return exchange account"""
    #     try:
    #         return (exchange.account
    #                 if isinstance(exchange, DexSwap)
    #                 else str(exchange.uid))
    #     except Exception as e:
    #         return f"⚠️ account: {e}"


    # async def get_account_balance():
    #     """return account balance."""
    #     balance = "🏦 Balance\n"
    #     try:
    #         if isinstance(exchange, DexSwap):
    #             balance += str(await exchange.get_account_balance())
    #         else:
    #             raw_balance = exchange.fetch_free_balance()
    #             filtered_balance = {k: v for k, v in
    #                                 raw_balance.items()
    #                                 if v is not None and v > 0}
    #             balance += "".join(f"{iterator}: {value} \n" for
    #                             iterator, value in
    #                             filtered_balance.items())
    #             if not balance:
    #                 balance += "No Balance"
    #         return balance
    #     except Exception as e:
    #         return f"⚠️ account_balance: {e}"


    # async def get_trading_asset_balance():
    #     """return main asset balance."""
    #     try:
    #         if isinstance(exchange, DexSwap):
    #             return await exchange.get_trading_asset_balance()
    #         else:
    #             return exchange.fetchBalance()[f"{settings.trading_asset}"]["free"]
    #     except Exception as e:
    #         return f"⚠️ Check balance {settings.trading_asset}: {e}"


    # async def get_account_position():
    #     """return account position."""
    #     try:
    #         if isinstance(exchange, DexSwap):
    #             open_positions = await exchange.get_account_position()
    #         else:
    #             open_positions = exchange.fetch_positions()
    #             open_positions = [p for p in open_positions if p['type'] == 'open']
    #         position = "📊 Position\n" + str(open_positions)
    #         position += str(await get_account_margin())
    #         return position
    #     except Exception as e:
    #         return f"⚠️ account_position: {e}"


    # async def get_account_margin():
    #     try:
    #         return "\n🪙 margin\n" + (
    #             str(0)
    #             if isinstance(exchange, DexSwap)
    #             else str(
    #                 await exchange.fetch_balance(
    #                     {
    #                         'type': 'margin',
    #                     }
    #                 )
    #             )
    #         )
    #     except Exception as e:
    #         return f"⚠️ account_margin: {e}"
