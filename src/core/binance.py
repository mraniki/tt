# -*- coding: utf-8 -*-
import ccxt
import time
import math
import json

from datetime import datetime
import calendar
import logging

import pandas as pd
pd.options.mode.chained_assignment = None

class Binance:

    SYMBOL = "ETH/BTC" # default symbol

    def __init__(self, symbol=SYMBOL, apiKey=None, secret=None, logger=None):
        self._exchange = ccxt.binance({"apiKey": apiKey, "secret": secret})
        self._symbol = symbol
        self._logger = logger if logger is not None else logging.getLogger(__name__)
        self._logger.info("class Binance initialized")

    def __del__(self):
        self._logger.info("class Binance deleted")

    def __get_error(self, e):
        ret = {"error": {"message": "{}".format(e), "name": "Binance.__get_error"}}
        return ret

    def ceil(self, price):
        return math.ceil(price * 2) / 2

    def floor(self, price):
        return math.floor(price * 2) / 2

    def open_orders(self, symbol=SYMBOL):

        orders = None

        try:
            orders = self._exchange.fetch_open_orders(symbol)
            self._logger.debug("- open orders={}".format(orders))
        except Exception as e:
            self._logger.error("- open orders: exception={}".format(e))
            orders = self.__get_error(e)

        return orders

    def limit_order(self, side, price, size):

        order = None
        order_id = str(time.time() * 1000)

        try:
            order = self._exchange.create_order(
                symbol=self._symbol,
                type="limit",
                side=side,
                amount=size,
                price=price,
                params={"newClientOrderId": "{}_limit_{}".format(order_id, side)},
            )
            self._logger.debug("- limit order={}".format(order))
        except Exception as e:
            self._logger.error("- limit order: exception={}".format(e))
            order = self.__get_error(e)

        return order

    def market_order(self, side, size):

        order = None
        order_id = str(round(time.time() * 1000))

        try:
            order = self._exchange.create_order(
                symbol=self._symbol,
                type="market",
                side=side,
                amount=size,
                params={"newClientOrderId": "{}_limit_{}".format(order_id, side)},
            )
            self._logger.debug("- market order={}".format(order))
        except Exception as e:
            self._logger.error("- market order: exception={}".format(e))
            order = self.__get_error(e)

        return order

    def cancel_order(self, orderId):

        order = None

        try:
            order = self._exchange.cancel_order(symbol=self._symbol, id=orderId)
            self._logger.debug("- cancel order={}".format(order))
        except Exception as e:
            self._logger.error("- cancel order: exception={}".format(e))
            order = self.__get_error(e)

        return order

    def cancel_orders(self):

        orders = None

        try:
            orders = self._exchange.fetch_open_orders()
            for i, o in enumerate(orders):
                if orders[i].get('status') == 'NEW':
                    orderId = orders[i].get('id')
                    self.cancel_order(orderId)
            self._logger.debug("- cancel orders={}".format(orders))
        except Exception as e:
            self._logger.error("- cancel orders: exception={}".format(e))
            orders = self.__get_error(e)

        return orders

    def balance(self):

        _balance = None

        try:
            _balance = self._exchange.fetch_balance()
            self._logger.debug("- balance={}".format(_balance))
        except Exception as e:
            self._logger.error("- balance: exception={}".format(e))
            _balance = self.__get_error(e)

        return _balance

    def position(self):

        _position = None

        try:
            _position = self._exchange.fapiPrivate_get_positionrisk()
            self._logger.debug("- position={}".format(_position))
        except Exception as e:
            self._logger.error("- position: exception={}".format(e))
            _position = self.__get_error(e)

        return _position

    def ticker(self, symbol=SYMBOL):

        _ticker = None
        try:
            _ticker = self._exchange.fetch_ticker(symbol=symbol)
            self._logger.debug("- ticker={}".format(_ticker))
        except Exception as e:
            self._logger.error("- ticker: exception={}".format(e))
            _ticker = self.__get_error(e)

        return _ticker

    def orderbook(self, symbol=SYMBOL, limit=100):

        _orderbook = None

        try:
            _orderbook = self._exchange.fetch_order_book(
                symbol=symbol, limit=limit
            )
            self._logger.debug("- orderbook={}".format(_orderbook))
        except Exception as e:
            self._logger.error("- orderbook: exception={}".format(e))
            _orderbook = self.__get_error(e)

        return _orderbook

    # returns ohlcv data, symbol and timeframe are mandatory
    def ohlcv(self, symbol=SYMBOL, timeframe="1m", since=None, limit=None, params={}):
        period = ["1m", "5m", "1h", "1d"]

        # timeframe must be one of period 1m 5m 1h 1d in this case
        if timeframe not in period:
            return None

        # configure retrieving limit, 100 is the minimum size
        fetch_count = 100 if limit is None else limit
        count = fetch_count

        ohlcvs = self._exchange.fetch_ohlcv(
            symbol=symbol, timeframe=timeframe, since=since, limit=count, params=params
        )

        return self.to_candleDF(ohlcvs)

    def to_candleDF(self, candle):
        df = pd.DataFrame(
            candle, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"], unit="ms", utc=True, infer_datetime_format=True
        )
        df = df.set_index("timestamp")
        return df

    def change_candleDF(self, ohlcv, resolution="1m"):
        period = {
            "1m": "1T",
            "3m": "3T",
            "5m": "5T",
            "15m": "15T",
            "30m": "30T",
            "1h": "1H",
            "2h": "2H",
            "3h": "3H",
            "4h": "4H",
            "6h": "6H",
            "12h": "12H",
            "1d": "1D",
            "3d": "3D",
            "1w": "1W",
            "2w": "2W",
            "1M": "1M",
        }

        if resolution not in period.keys():
            return None

        df = (
            ohlcv[["open", "high", "low", "close", "volume"]]
            .resample(period[resolution], label="left", closed="left")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
        )

        return df
