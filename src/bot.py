##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.6.24"

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

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##============= variables  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#IMPORT ENV FILE (if you are using .env file)

path = sys.path[1]+'/config/.env'  #try .path[0] if 1 doesn't work
load_dotenv(path)

# ENV VAR (from file or docker variable)
TG_TOKEN = os.getenv('TG_TOKEN')
TG_USER_ID = os.getenv("TG_USER_ID")
print (TG_TOKEN)
print (TG_USER_ID)

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
    CCXT_ex = f'{CCXT_test_name}'
    exchange_class = getattr(ccxt, CCXT_ex)
    exchange = exchange_class({
        'apiKey': CCXT_test_api,
        'secret': CCXT_test_secret,
    })
    type=CCXT_test_ordertype  # update to limit for limit order
    exchange.set_sandbox_mode(CCXT_test_mode)
    exchange.load_markets()
else:
    CCXT_ex = 'binance'
    exchange_class = getattr(ccxt, CCXT_ex)
    exchange = exchange_class({
        'apiKey': CCXT_id1_api,
        'secret': CCXT_id1_secret,
        'password': CCXT_id1_password
    })
    type=CCXT_id1_ordertype  # update to limit for limit order
    exchange.load_markets()

print (f"exchange setup done for {exchange.name}")

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

exchangeinfo= f'{exchange.name}  {exchange.version}'

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== help  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#     
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f" {TTVersion} \n /{commandlist}  \n exchange configured: {exchangeinfo}  \n ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## ========== startup message   ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def post_init(application: Application):
    await application.bot.send_message(user_id, f"Bot is online {TTVersion} \n /{commandlist}")
    #help_command()
   
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
    balancerawjson = exchange.fetch_free_balance()
    balancenonzerobal = {k: v for k, v in balancerawjson.items() if v > 0}
    print (balancenonzerobal)
    balancetodisplay = json.dumps(balancenonzerobal, sort_keys=True, indent=4)
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
   #  balance = ccxt_ex_1.fetch_balance()
   #  positions = balance['info']['positions']
   #  pprint(positions)
   # #lastclosedorder
   #  await update.message.reply_text(f" list of positions {positions}")    

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======= view last closed orders  =====
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

    
# def get_balances_from_api() -> dict:
#     load_dotenv()
#     exchange = ccxt.exchangeid({
#         'apiKey': os.getenv('API_KEY'),
#         'secret': os.getenv('SECRET'),
#         'password': os.getenv('PASSWORD')
#     })
#     balances_ = exchange.fetch_balance()
#     columns_ = ['id', 'currency', 'account_type', 'balance', 'available', 'holds']
#     data_ = []
#     for data in balances_['info']['data']:
#         data_.append([
#             data['id'], data['currency'], data['type'],
#             data['balance'], data['available'], data['holds']
#         ])
#     df_ = pd.DataFrame(data=data_, columns=columns_)
#     df_.set_index('id', drop=True, inplace=True)
#     return df_.to_dict()
  
