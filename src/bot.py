##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.6.26"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== import  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

##log
import logging
import sys

##env
import os
import argparse
from dotenv import load_dotenv
from dotenv import find_dotenv
from dotenv import dotenv_values

from os import getenv
from pathlib import Path
import itertools

#telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

#ccxt
import ccxt
import json

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

def free_balance(self):
    balance = self.fetch_free_balance()
    # surprisingly there are balances with 0, so we need to filter these out
    return {k: v for k, v in balance.items() if v > 0}

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##============= variables  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#IMPORT ENV FILE (if you are using .env file)
env_file = find_dotenv(".env")
load_dotenv(env_file)
#variables=dotenv_values(".env")

# ENV VAR (from file or docker variable)
TG_TOKEN = os.getenv("TG_TOKEN")
TG_USER_ID = os.getenv("TG_USER_ID")

CCXT_id1_name = os.getenv("EXCHANGE1_NAME")
CCXT_id1_api = os.getenv("EXCHANGE1_YOUR_API_KEY")  
CCXT_id1_secret = os.getenv("EXCHANGE1_YOUR_SECRET") 
CCXT_id1_password = os.getenv("EXCHANGE1_YOUR_PASSWORD") 
CCXT_id1_ordertype = os.getenv("EXCHANGE1_ORDERTYPE") 

#CCXT SANDBOX details
CCXT_test_mode = os.getenv("TEST_SANDBOX_MODE")
CCXT_test_name = os.getenv("TEST_SANDBOX_EXCHANGE_NAME")  
CCXT_test_api = os.getenv("TEST_SANDBOX_YOUR_API_KEY") 
CCXT_test_secret = os.getenv("TEST_SANDBOX_YOUR_SECRET") 
CCXT_test_ordertype = os.getenv("TEST_SANDBOX_ORDERTYPE") 

trading=True #trading switch command


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== exchange setup  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging and version check
#EXCHANGE1 from variable id

if CCXT_test_mode == True:
    try:
     CCXT_ex = 'binance'
     exchange_class = getattr(ccxt, CCXT_ex)
     exchange = exchange_class({
        'apiKey': CCXT_test_api,
        'secret': CCXT_test_secret
        })
     type=CCXT_test_ordertype
     exchange.set_sandbox_mode(CCXT_test_mode)
     exchange.load_markets()
     print (f"exchange setup done for {exchange.name}")
    except NameError:
     error_handler()
     
else:
    try:
     CCXT_ex = 'binance'
     exchange_class = getattr(ccxt, CCXT_ex)
     exchange = exchange_class({
        'apiKey': CCXT_id1_api,
        'secret': CCXT_id1_secret})
     exchange.load_markets()
     type=CCXT_id1_ordertype 
     print (f"exchange setup done for {exchange.name}")
    except NameError:
     error_handler()

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##= telegram bot commands and messages==
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


user_id = TG_USER_ID
##list of commands 
command1=['help']
command2=['bal']
command3=['order']
command4=['trading']
#command5=['pastorders']
listofcommand = list(itertools.chain(command1, command2, command3, command4))
commandlist= ' /'.join([str(elem) for elem in listofcommand])

####messages

exchangeinfo= f'ℹ️exchange configured: {exchange.name}  Sandbox: {CCXT_test_mode}'

menu=f'{TTVersion} \n /{commandlist} \n'

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== help  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f"{menu} \n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## ========== startup message   ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def post_init(application: Application):
    await application.bot.send_message(user_id, f"Bot is online ")
    #help_command()
   
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##===== order parsing and placing  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

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
         #res = exchange1.market_order(m_dir, m_symbol, m_q)
         res = exchange.create_order(m_symbol, type, m_dir, m_q)
         
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
          await update.message.reply_text(f"🟢 ORDER PLACED \n order id {orderid} @ {timestamp} \n  {side} {symbol} {amount} @ {price}")
          return orderid
    else: error_handler

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##========== view balance  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /bal is issued."""
    # balancerawjson = await free_balance(exchange)
    # print (balancerawjson)
    balance = exchange.fetch_free_balance()
    print(balance)
    balancefiltered= {k: v for k, v in balance.items() if v > 0}
    print(balancefiltered)
    balancetodisplay = json.dumps(balancefiltered, sort_keys=True, indent=4)
    print (balancetodisplay)
    balanceloaded = json.loads(balancetodisplay)
    prettybal=""
    for iterator in balanceloaded:
     print(iterator, ":", balanceloaded[iterator])
     prettybal += (f"{iterator} : {balanceloaded[iterator]} \n")
    await update.message.reply_text(f"🏦 Balance \n{prettybal}")
    
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view positions  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def orderlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /order is issued."""


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======= view last closed orders  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# 


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view today's pnl =========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# 


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
    print ("----- ERROR -----")
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text(f"Error encountered {context.error}")
    
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== BOT  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

def main():

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_TOKEN).post_init(post_init).build()

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


  
