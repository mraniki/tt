from cefi import CexTrader
from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin


class UnifiedExchangePlugin(BasePlugin):
    """
    Class ExchangePlugin
    to support CEX and DEX Exchange
    More info: https://github.com/mraniki/cefi
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
        Initializes a new instance of the class.

        This method is called when an object of
        the class is created.
        It sets the `enabled` attribute
        to the value of `settings.cex_enabled`
        and/or `settings.dxsp_enabled`.
        If any of them is `False`,
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
        self.enabled_dex, self.enabled_cex = settings.dxsp_enabled, settings.cex_enabled
        self.enabled = self.enabled_dex or self.enabled_cex

        if self.enabled:
            self.fmo = FindMyOrder()
            self.exchange_dex = DexSwap() if self.enabled_dex else None
            self.exchange_cex = CexTrader() if self.enabled_cex else None

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
                self.bot_command_info: self.get_info,
                self.bot_command_bal: self.get_balances,
                self.bot_command_pos: self.get_positions,
                self.bot_command_quote: lambda: self.get_quotes(args[0]),
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")

        elif await self.fmo.search(msg) and not self.should_handle_timeframe():
            await self.send_notification(self.trading_control_message)

        elif await self.fmo.search(msg) and self.should_handle_timeframe():
            order = await self.fmo.get_order(msg)
            if order and self.trading_enabled:
                trade = await self.submit_order(order)
                if trade:
                    await self.send_notification(trade)

    async def get_info(self):
        """
        Retrieves and combines information from both DEX and CEX.
        """
        info = []
        if self.fmo:
            info.append(await self.fmo.get_info())
        if self.exchange_dex:
            info.append(await self.exchange_dex.get_info())
        if self.exchange_cex:
            info.append(await self.exchange_cex.get_info())
        return "\n".join(info)

    async def get_quotes(self, symbol=None):
        """
        Retrieves quotes for a given symbol from both DEX and CEX.
        """
        quotes = ["⚖️"]
        if symbol and self.exchange_dex:
            quotes.append(await self.exchange_dex.get_quotes(symbol))
        if symbol and self.exchange_cex:
            quotes.append(await self.exchange_cex.get_quotes(symbol))
        return "\n".join(quotes)

    async def get_balances(self):
        """
        Retrieves and combines balances from both DEX and CEX.
        """
        balances = ["🏦"]
        if self.exchange_dex:
            balances.append(await self.exchange_dex.get_balances())
        if self.exchange_cex:
            balances.append(await self.exchange_cex.get_balances())
        return "\n".join(balances)

    async def get_positions(self):
        """
        Retrieves and combines positions from both DEX and CEX.
        """
        positions = ["📊"]
        if self.exchange_dex:
            positions.append(await self.exchange_dex.get_positions())
        if self.exchange_cex:
            positions.append(await self.exchange_cex.get_positions())
        return "\n".join(positions)

    # async def get_pnl(self):
    #     """
    #     Retrieves and combines positions from both DEX and CEX.
    #     """
    #     pnl = ["🏆"]
    #     if self.exchange_dex:
    #         pnl.append(await self.exchange_dex.get_pnls())
    #     if self.exchange_cex:
    #         pnl.append(await self.exchange_cex.get_pnls())
    #     return "\n".join(pnl)

    async def submit_order(self, order):
        """
        Submits an order using the appropriate exchange.
        """
        order_results = ["🧾"]
        if self.enabled_dex:
            order_results.append(await self.exchange_dex.submit_order(order))
        if self.enabled_cex:
            order_results.append(await self.exchange_cex.submit_order(order))
        return "\n".join(order_results)
