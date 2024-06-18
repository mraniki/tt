from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin


class DexExchangePlugin(BasePlugin):
    """
    Class DexExchangePlugin
    to support DexSwap object
    built via DXSP lib
    More info: https://github.com/mraniki/dxsp
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
        Initializes the object.

        This method initializes the object
        and sets the `enabled` attribute based on
        the value of `settings.dxsp_enabled`.
        If `settings.dxsp_enabled` is `False`,
        the method returns without further execution.
        Otherwise, it creates an instance of
        the `FindMyOrder` class and assigns
        it to the `fmo` attribute.
        It also creates an instance of the `DexSwap` class
        and assigns it to the `exchange` attribute.

        Parameters:
            None

        Returns:
            None
        """
        super().__init__()
        self.enabled = settings.dxsp_enabled
        if not self.enabled:
            return
        self.fmo = FindMyOrder()
        self.exchange = DexSwap()

    async def handle_message(self, msg):
        """
        Handles incoming messages and
        routes them to the appropriate function.

        Args:
            msg (str): The message received by the plugin.

        Supported functions are:

        - `get_info()`
        - `get_balances()`
        - `get_positions()`
        - `get_quotes()`
        - `submit_order()`

        """

        if self.should_filter(msg):
            return

        elif self.is_command_to_handle(msg):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                settings.bot_command_info: self.exchange.get_info,
                settings.bot_command_bal: self.exchange.get_balances,
                settings.bot_command_pos: self.exchange.get_positions,
                settings.bot_command_quote: lambda: self.exchange.get_quotes(args[0]),
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

        elif await self.fmo.search(msg) and not self.should_handle_timeframe():
            await self.send_notification("⚠️ Trading restricted")

        elif await self.fmo.search(msg) and self.should_handle_timeframe():
            order = await self.fmo.get_order(msg)
            if order and settings.trading_enabled:
                trade = await self.exchange.submit_order(order)
                if trade:
                    await self.send_notification(trade)
