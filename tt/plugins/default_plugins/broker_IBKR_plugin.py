import os

from findmyorder import FindMyOrder
from ib_insync import IB, Client

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class Broker_IBKR_Plugin(BasePlugin):
    """
    Support IBKR Broker via BrokerExchange object
    
    Order are identified and parsed using Findmyorder lib
    More info: https://github.com/mraniki/findmyorder

    Args:
        None

    Returns:
        None

    """

    name = os.path.splitext(os.path.basename(__file__))[0]

    def __init__(self):
        super().__init__()
        self.enabled = settings.broker_enabled
        if self.enabled:
            self.fmo = FindMyOrder()
            self.exchange = BrokerExchange()
            logger.debug("Broker_IBKR_Plugin initialized")

    async def start(self):
        """Starts the broker_plugin plugin"""

    async def stop(self):
        """Stops the broker_plugin plugin"""

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """
        Handles incoming messages
        to route to the respective function

        Args:
            msg (str): The incoming message

        Returns:
            None

        """
        if not self.should_handle(msg):
            return
        logger.debug("settings.bot_ignore: {}", settings.bot_ignore)
        if settings.bot_ignore not in msg or settings.bot_prefix not in msg:
            if await self.fmo.search(msg):
                order = await self.fmo.get_order(msg)
                if order and settings.trading_enabled:
                    trade = await self.exchange.submit_order(order)
                    if trade:
                        await send_notification(trade)

        if msg.startswith(settings.bot_prefix):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.exchange.get_info,
                settings.bot_command_quote: lambda: self.exchange.get_quote(args[0]),
                settings.bot_command_bal: self.exchange.get_balance,
                settings.bot_command_pos: self.exchange.get_position,
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")


class BrokerExchange:
    """
    Class BrokerExchange to support IBKR Broker
    built via ib_insync library
    More info: https://github.com/erdewit/ib_insync

    """

    def __init__(self):
        self.ib = IB()
        self.client = Client()
        self.ib.connect()

    def get_info(self):
        pass

    def get_quote(self, symbol):
        pass

    def get_balance(self):
        pass

    def get_position(self):
        pass

    def submit_order(self, order):
        pass
        # try:
        #     contract = order["instrument"]
        #     trade = self.exchange.placeOrder(contract, order)
        #     return trade
        # except RuntimeError:
        #     return None
