from ccxt import Exchange, OrderNotFound
from datetime import datetime
import time
import logging



class CryptoExchange:





    def __init__(self, exchange: Exchange,logger=None):
        self.exchange = exchange
        self.exchange.set_sandbox_mode(True)  # comment if you're not using the testnet
        self.exchange.verbose = True  # debug output
        self.exchange.load_markets()
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.logger.info("class CryptoExchange initialized")

    @property
    def free_balance(self):
        balance = self.exchange.fetch_free_balance()
        # surprisingly there are balances with 0, so we need to filter these out
        return {k: v for k, v in balance.items() if v > 0}

    def fetch_open_orders(self, symbol: str = None):
        return self.exchange.fetch_open_orders(symbol=symbol)

    def fetch_order(self, order_id: int):
        return self.exchange.fetch_order(order_id)

    def cancel_order(self, order_id: int):
        try:
            self.exchange.cancel_order(order_id)
        except OrderNotFound:
            # treat as success
            pass
    def __get_error(self, e):
        ret = {"error": {"message": "{}".format(e), "name": "Binance.__get_error"}}
        return ret

    def create_marketorder(self, side: str, symbol: str, amount: float):
        return self.exchange.create_order(symbol=symbol, type="market", side=side, amount=amount)

    def market_order(self, side, symbol, amount):

        order = None

        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=amount,
            )
            self.logger.debug("- market order={}".format(order))
        except Exception as e:
            self.logger.error("- market order: exception={}".format(e))
            order = self.__get_error(e)

        return order

    def balance(self):

        balance = None

        try:
            balance = self.exchange.fetch_balance()
            self.logger.debug("- balance={}".format(_balance))
        except Exception as e:
            self.logger.error("- balance: exception={}".format(e))
            balance = self.__get_error(e)

        return balance
