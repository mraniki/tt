# plugin being added to CEFI library instead

# import os

# from findmyorder import FindMyOrder
# from ib_insync import IB, Forex, Order

# from tt.config import logger, settings
# from tt.plugins.plugin_manager import BasePlugin
# from tt.utils import send_notification


# class Broker_IBKR_Plugin(BasePlugin):
#     """
#     Support IBKR Broker via BrokerExchange object

#     Order are identified and parsed using Findmyorder lib
#     More info: https://github.com/mraniki/findmyorder

#     Args:
#         None

#     Returns:
#         None

#     """

#     name = os.path.splitext(os.path.basename(__file__))[0]

#     def __init__(self):
#         super().__init__()
#         self.enabled = settings.broker_enabled
#         if self.enabled:
#             self.fmo = FindMyOrder()
#             self.exchange = BrokerExchange()

#     async def start(self):
#         """Starts the broker_plugin plugin"""

#     async def stop(self):
#         """Stops the broker_plugin plugin"""

#     async def send_notification(self, message):
#         """Sends a notification"""
#         if self.enabled:
#             await send_notification(message)

#     async def handle_message(self, msg):
#         """
#         Handles incoming messages
#         to route to the respective function

#         Args:
#             msg (str): The incoming message

#         Returns:
#             None

#         """
#         if not self.should_handle(msg):
#             return
#         logger.debug("settings.bot_ignore: {}", settings.bot_ignore)
#         if settings.bot_ignore not in msg or settings.bot_prefix not in msg:
#             if await self.fmo.search(msg):
#                 order = await self.fmo.get_order(msg)
#                 if order and settings.trading_enabled:
#                     trade = await self.exchange.submit_order(order)
#                     if trade:
#                         await send_notification(trade)

#         if msg.startswith(settings.bot_prefix):
#             command, *args = msg.split(" ")
#             command = command[1:]

#             command_mapping = {
#                 settings.bot_command_info: self.exchange.get_info,
#                 settings.bot_command_quote: lambda: self.exchange.get_quote(args[0]),
#                 settings.bot_command_bal: self.exchange.get_balance,
#                 settings.bot_command_pos: self.exchange.get_position,
#             }

#             if command in command_mapping:
#                 function = command_mapping[command]
#                 await self.send_notification(f"{await function()}")


# class BrokerExchange:
#     """
#     Class BrokerExchange to support IBKR Broker
#     built via ib_insync library
#     More info: https://github.com/erdewit/ib_insync

#     """

#     def __init__(self):
#         """
#         Initializes the Broker_IBKR_Plugin class.

#         This function creates an instance of the IB class from the ib_insync
#         library and sets it as the 'ib' attribute of the class.
#         It also sets the 'client' attribute to None as a placeholder
#         for actual client details.

#         To connect to the Interactive Brokers (IBKR) platform,
#         the 'connect' method of the 'ib' instance is called.
#         This method requires the host, port, and clientId as parameters.
#         In this case, the function connects to the IBKR platform using
#         the IP address "127.0.0.1", port 7497, and clientId 1.

#         After successfully connecting to IBKR, the function logs
#         a debug message using the logger module.

#         Parameters:
#         - None

#         Return Type:
#         - None
#         """
#         self.ib = IB()
#         self.ib.connect(
#             host=settings.broker_host or "127.0.0.1",
#             port=settings.broker_port or 7497,
#             clientId=settings.broker_clientId or 1,
#             readonly=settings.broker_read_only or False,
#             account=settings.broker_account_number or "",
#         )

#         logger.debug("Connected to IBKR {}", self.ib.isConnected())
#         self.account = self.ib.managedAccounts()[0]
#         logger.debug("Broker_IBKR_Plugin initialized with account: {}", self.account)

#     def get_info(self):
#         """
#         Retrieves information from the accountValues method of the `ib` object.

#         Returns:
#             The result of calling the accountValues method of the `ib` object.
#         """
#         return self.ib.accountValues()

#     def get_quote(self, symbol):
#         """
#         Retrieves a quote for a given symbol from the Interactive Brokers API.

#         Args:
#             symbol (str): The symbol of the forex contract.

#         Returns:
#             ticker: The ticker representing the quote for the given symbol.
#         """
#         contract = Forex(symbol, "SMART", "USD")
#         self.ib.reqMktData(contract)
#         return self.ib.ticker(contract)

#     def get_balance(self):
#         """
#         Get the balance of the account.

#         Returns:
#             The balance of the account.
#         """
#         return self.ib.accountSummary(self.account)

#     def get_position(self):
#         """
#         Get the position of the current object.
#         :return: A list of positions.
#         """
#         return self.ib.positions()

#     def submit_order(self, order_details):
#         """
#         Submit an order to the trading platform.

#         Parameters:
#             order_details (dict): A dictionary containing the details of the order.
#                 - instrument (str): The instrument to trade.
#                 - action (str): The action to perform, either 'BUY' or 'SELL'.
#                 - order_type (str, optional): The type of order. Defaults to 'MKT'.
#                 - quantity (int): The quantity of the order.

#         Returns:
#             trade: The result of the order placement.

#         Raises:
#             RuntimeError: If the order submission fails.

#         """
#         try:
#             # todo: add support for limit price
#             # todo: add support for multiple contract type
#             contract = Forex(order_details["instrument"], "SMART", "USD")
#             # Create an Order object
#             order = Order()
#             order.action = order_details["action"]  # 'BUY' or 'SELL'
#             order.orderType = order_details["order_type"] or "MKT"
#             order.totalQuantity = order_details["quantity"]

#             return self.ib.placeOrder(contract, order)
#         except Exception as e:
#             logger.error(f"Order submission failed: {e}")
#             return None
