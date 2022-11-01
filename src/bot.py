##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.6.16"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== import  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

import logging
import sys
import os
import argparse
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import itertools

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import ccxt
from core.exchange import CryptoExchange
import json
import pandas as pd

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== Logging  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging and version check

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
def log(severity, msg):
   logger.log(severity, msg)

print(TTVersion)
print('python', sys.version)
print('CCXT Version:', ccxt.__version__)
print('Please wait while the program is loading...')

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##====== common functions  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

def Convert(string):
   li = list(string.split(" "))
   return li

   
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##============= variables  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#IMPORT ENV FILE (if you are using .env file)
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# ENV VAR (from file or docker variable)
telegram_tkn = os.getenv("TOKEN")
ALLOWED_USER_ID = getenv("ALLOWED_USER_ID")
parser = argparse.ArgumentParser(description="INT Transformation")
parser.add_argument("--user-id", required=False, type=int, default=ALLOWED_USER_ID)
args = parser.parse_args()
user_id = args.user_id
print(user_id)

exchange_id1_sandbox = getenv("SANDBOX_MODE")
exchange_id1 = getenv("EXCHANGE1")
exchange_id1_api = getenv("EXCHANGE1YOUR_API_KEY")  
exchange_id1_secret = getenv("EXCHANGE1YOUR_SECRET") 

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== exchange setup  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging and version check
#EXCHANGE1 from variable id
exchange_id = exchange_id1
exchange_class = getattr(ccxt, exchange_id)
ccxt_ex_1 = exchange_class({
    'apiKey': exchange_id1_api,
    'secret': exchange_id1_secret,
})

#ex1 setup
exchange1 = CryptoExchange(ccxt_ex_1)
ccxt_ex_1.set_sandbox_mode(exchange_id1_sandbox)
print ("ex1 setup done")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=== telegram bot / commands   =======
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging and version check

##list of commands 
command1=['help']
command2=['bal']
command3=['order']
command4=['trading']
#command5=['pastorders']
listofcommand = list(itertools.chain(command1, command2, command3, command4))
commandlist= ' /'.join([str(elem) for elem in listofcommand])
trading=True #trading switch command

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== help  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f" {TTVersion} \n /{commandlist} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## ========== startup message   ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def post_init(application: Application):
    await application.bot.send_message(user_id, f"Bot is online \n {TTVersion} \n /{commandlist}")
   
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##===== order parsing and placing  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when an order is identified """
    messagetxt = update.message.text
    messagetxt_upper =messagetxt.upper()
    filter_lst = ['BUY', 'SELL', 'TEST']
    if [ele for ele in filter_lst if(ele in messagetxt_upper)]:
      if (trading==False):
         await update.message.reply_text("TRADING IS DISABLED")
      else:
         order_m = Convert(messagetxt_upper)
         # sell BTCUSDT sl=6000 tp=4500 q=1%
         m_dir= order_m[0]
         m_symbol=order_m[1]
         m_sl=order_m[2][3:6]
         m_tp=order_m[3][3:6]
         m_q=order_m[4][2:-1]
         print (m_dir,m_symbol,m_sl,m_tp,m_q)
         await update.message.reply_text("THIS IS AN ORDER TO PROCESS")
         print ("processing order")
         res = exchange1.market_order(m_dir, m_symbol, m_q)
         if "error" in res:
            await update.message.reply_text(f"{res}")
         else: 
          orderid=res['id']
          timestamp=res['datetime']
          symbol=res['symbol']
          side=res['side']
          amount=res['amount']
          price=res['price']
          #orderdetails=orderid + timestamp + symbol + side +amount + price
          await update.message.reply_text(f"ORDER PLACED SUCCESSFULLY \n {orderid} \n {timestamp} \n {symbol} \n {side} \n {amount} \n {price} ")
          return orderid
    else: error_handler

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##========== view balance  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /bal is issued."""
    balancerawjson = exchange1.free_balance
    print (balancerawjson)
    balancetodisplay = json.dumps(balancerawjson, sort_keys=True, indent=4)
    print (balancetodisplay)
    balanceloaded = json.loads(balancetodisplay)
    prettybal=""
    for iterator in balanceloaded:
     print(iterator, ":", balanceloaded[iterator])
     prettybal += (f"{iterator} : {balanceloaded[iterator]} \n")
     #test+=(f iterator ":" loaded[iterator] "\n")
    await update.message.reply_text(f"🏦 Balance \n{prettybal}")
    
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view open orders  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def orderlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /order is issued."""
    openorder1 = exchange1.fetch_open_orders("BTC/USDT")
   #lastclosedorder
    await update.message.reply_text(f" list of orders {openorder1}")    


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view closed orders  =======
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# 
# async def closedorderlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     symbolClosed = 'ETH/USDT'
#     now = exchange1.milliseconds()
#     day = 24 * 3600 * 1000
#     week = 7 * day
#     since = now - 7 * day  # start 1 week
#     limit = 20

#     while since < now:

#         end = min(since + week, now)
#         params = {'endAt': end}
#         closedorders = exchange1.fetch_closed_orders(symbolClosed, since, limit, params)
#         print(exchange1.iso8601(since), '-', exchange1.iso8601(end), len(orders), 'orders')
#         if len(closedorders) == limit:
#             since = orders[-1]['timestamp']
#         else:
#             since += week
#         await update.message.reply_text(f"{exchange1.iso8601(since)} '-' {exchange1.iso8601(end)} '-' {len(orders)} 'orders'")  


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== trading switch  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def trading_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /trading is issued."""
    global trading
    if (trading==False):
      trading=True
      await update.message.reply_text(f"Trading is {trading}")
    else:
      trading=False
      await update.message.reply_text(f"Trading is {trading}")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========  bot error handling ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(f"Error encountered {context.error}")
    
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== BOT  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

def main():

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_tkn).post_init(post_init).build()

    # Menus
    application.add_handler(CommandHandler(command1, help_command))
    application.add_handler(CommandHandler(command2, bal_command))
    application.add_handler(CommandHandler(command3, orderlist_command))
    #application.add_handler(CommandHandler(command5, closedorderlist_command))
    application.add_handler(CommandHandler(command4, trading_switch))
    # Message monitoring for order
    application.add_handler(MessageHandler(filters.ALL, monitor))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
