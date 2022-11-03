##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.7.0"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== import  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

##log
import logging
import sys
import traceback

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
print('Please wait, loading...')

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##====== common functions  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

def Convert(string):
   li = list(string.split(" "))
   return li

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##============= variables  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#IMPORT ENV  

dotenv_path = './config/.env'
if os.path.exists(dotenv_path):
    print("env file found")
    load_dotenv(dotenv_path)
#for env debug    print(json.dumps({**{}, **os.environ}, indent=2)) 
else:
    print("no env file available check the path for config")
#for env debug    print(json.dumps({**{}, **os.environ}, indent=2)) 
    sys.exit()


# ENV VAR (from file or docker variable)
TG_TOKEN = os.getenv("TG_TOKEN")
TG_USER_ID = os.getenv("TG_USER_ID")

CCXT_id1_name = os.getenv("EXCHANGE1_NAME")
CCXT_id1_api = os.getenv("EXCHANGE1_YOUR_API_KEY")  
CCXT_id1_secret = os.getenv("EXCHANGE1_YOUR_SECRET") 
CCXT_id1_password = os.getenv("EXCHANGE1_YOUR_PASSWORD") 
CCXT_id1_ordertype = os.getenv("EXCHANGE1_ORDERTYPE")
CCXT_id1_defaulttype = os.getenv("EXCHANGE1_DEFAULTTYPE")
#'defaultType': 'future'

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

if (CCXT_test_mode=="True"):
    print ("sandbox activated")
    try:
     CCXT_ex = f'{CCXT_test_name}'
     exchange_class = getattr(ccxt, CCXT_ex)
     exchange = exchange_class({
        'apiKey': CCXT_test_api,
        'secret': CCXT_test_secret
        })
     m_ordertype = CCXT_test_ordertype.upper()
     exchange.set_sandbox_mode(CCXT_test_mode)
     print (f"exchange setup done for {exchange.name} sandbox")
    except NameError:
     error_handler()
     
else:
    try:
     CCXT_ex = f'{CCXT_id1_name}'
     exchange_class = getattr(ccxt, CCXT_ex)
     exchange = exchange_class({
        'apiKey': CCXT_id1_api,
        'secret': CCXT_id1_secret,
        'options': {
        'defaultType': CCXT_id1_defaulttype,
        },
     })
     m_ordertype = CCXT_test_ordertype.upper()
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
menu=f'{TTVersion} \n /{commandlist}'
exchangeinfo= f'Exchange: {exchange.name}  Sandbox: {CCXT_test_mode}'

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
    await application.bot.send_message(user_id, f"Bot is online\n{menu}\n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##===== order parsing and placing  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when an order is identified """
    messagetxt = update.message.text
    print(messagetxt)
    messagetxt_upper =messagetxt.upper()
    print(messagetxt_upper)
    filter_lst = ['BUY', 'SELL', 'TEST']
    if [ele for ele in filter_lst if(ele in messagetxt_upper)]:
      if (trading==False):
         await update.message.reply_text("TRADING IS DISABLED")
      else:
         order_m = Convert(messagetxt_upper)
         # sell BTCUSDT sl=6000 tp=4500 q=1%
         m_dir= order_m[0]
         m_symbol=order_m[1]
         m_sl=order_m[2][3:7]
         m_tp=order_m[3][3:7]
         m_q=order_m[4][2:-1]
         print (m_symbol,m_ordertype,m_dir,m_sl,m_tp,m_q)
         await update.message.reply_text("THIS IS AN ORDER TO PROCESS")
         print ("processing order")
         
         #calculate percentage 
         amountpercent=(exchange.fetch_free_balance('USDT')*(m_q/100))
         res = exchange.create_order(m_symbol, m_ordertype, m_dir, amountpercent)
         
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
    balance = exchange.fetch_free_balance()
    print(balance)
    prettybal=""
    for iterator in balance:
     print(iterator, ":", balance[iterator])
     prettybal += (f"{iterator} : {balance[iterator]} \n")
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
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:4000]
    await update.message.reply_text(f"Error encountered {tb_trim}")
    
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


  
