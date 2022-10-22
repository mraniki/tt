import logging
import os
import ccxt

from core.exchange import CryptoExchange
from core.telegrambot import TelegramBot
from core.tradeexecutor import TradeExecutor

from os import getenv

message = 'Please wait while the program is loading...'
print(message)


# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

telegram_tkn = getenv("TOKEN")
user_id = getenv("ALLOWED_USER_ID")
exchange_id = getenv("EXCHANGE1")
exchange_id1_api = getenv("EXCHANGE1YOUR_API_KEY")  
exchange_id1_secret = getenv("EXCHANGE1YOUR_SECRET") 


exchange_class = getattr(ccxt, exchange_id)
ccxt_ex = exchange_class({
    'apiKey': exchange_id1_api,
    'secret': exchange_id1_secret,
})


exchange = CryptoExchange(ccxt_ex)
trade_executor = TradeExecutor(exchange)
telegram_bot = TelegramBot(telegram_tkn, user_id, trade_executor)

telegram_bot.start_bot()
print(exchange.fetch_balance())
