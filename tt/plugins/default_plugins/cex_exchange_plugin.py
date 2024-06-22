from cefi import CexTrader
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin


class CexExchangePlugin(BasePlugin):
    """
    Class CexExchangePlugin
    to support CEX Exchange
    built via Cefi lib
    More info: https://github.com/mraniki/cefi
    Order are identified and parsed
    using Findmyorder lib
    More info: https://github.com/mraniki/findmyorder

    Args:
        None

    Returns:
        None

    """

    def __init__(self):
        """
        Initializes a new instance of the class.

        This method is called when an object of
        the class is created.
        It sets the `enabled` attribute
        to the value of `settings.cex_enabled`.
        If `settings.cex_enabled` is `False`,
        the method returns early and no further
        initialization is performed. Otherwise,
        it creates an instance of the `FindMyOrder`
        class and assigns it to the `fmo` attribute.
        It also creates an instance of the `CexTrader`
        class and assigns it to the `exchange` attribute.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.enabled = settings.cex_enabled
        if not self.enabled:
            return
        self.fmo = FindMyOrder()
        self.exchange = CexTrader()

    async def handle_message(self, msg):
        """
        Handles incoming messages and
        routes them to the appropriate function.

        Args:
            msg (str): The message received by the plugin.

        Supported functions are:

        - `get_info()`
        - `get_quotes()`
        - `get_balances()`
        - `get_positions()`

        """

        if self.should_filter(msg):
            return

        elif self.is_command_to_handle(msg):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                self.bot_command_info: self.exchange.get_info,
                self.bot_command_bal: self.exchange.get_balances,
                self.bot_command_pos: self.exchange.get_positions,
                self.bot_command_quote: lambda: self.exchange.get_quotes(args[0]),
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

        elif await self.fmo.search(msg) and not self.should_handle_timeframe():
            await self.send_notification(self.trading_control_message)

        elif await self.fmo.search(msg) and self.should_handle_timeframe():
            order = await self.fmo.get_order(msg)
            if order and self.trading_enabled:
                trade = await self.exchange.submit_order(order)
                if trade:
                    await self.send_notification(trade)
