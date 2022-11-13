##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.8.7"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== import  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

##log
import logging
import sys
import traceback
from threading import Thread
import time

##env
import os
import argparse
from dotenv import load_dotenv

from os import getenv
from pathlib import Path
import itertools

#telegram
from telegram import Update    
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

#ccxt
import ccxt
import json

#db
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== Logging  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
# def log(severity, msg):
#    logger.log(severity, msg)
logger.info(msg=f"{TTVersion}")
logger.info(msg=f"python {sys.version}")
logger.info(msg=f"CCXT Version: {ccxt.__version__}")
logger.info(msg=f"Please wait, loading...")

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
    logger.info(msg=f"env file found")
    load_dotenv(dotenv_path)
    #environementinfo={json.dumps({**{}, **os.environ}, indent=2)}
    #logger.info(msg=f"{environementinfo}")  
else:
    logger.info(msg=f"no env file available check the path for config")
    environementinfo={json.dumps({**{}, **os.environ}, indent=2)}
    logger.info(msg=f"{environementinfo}") 
    sys.exit()

# ENV VAR (from file or docker variable)
TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")

CCXT_id1_name = os.getenv("EXCHANGE1_NAME")
CCXT_id1_api = os.getenv("EXCHANGE1_YOUR_API_KEY")  
CCXT_id1_secret = os.getenv("EXCHANGE1_YOUR_SECRET") 
CCXT_id1_password = os.getenv("EXCHANGE1_YOUR_PASSWORD") 
CCXT_id1_ordertype = os.getenv("EXCHANGE1_ORDERTYPE")
CCXT_id1_defaulttype = os.getenv("EXCHANGE1_DEFAULTTYPE")
CCXT_test_mode = os.getenv("EXCHANGE1_SANDBOX_MODE")

if (TG_TOKEN==""):
    logger.info(msg=f"missing telegram token")
    sys.exit()
elif (CCXT_id1_name==""):
    logger.info(msg=f"missing main exchangeinfo")
    sys.exit()
elif (CCXT_id1_name==""):
    logger.info(msg=f"no sandbox setup")


    
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== DB SETUP =================
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
db = TinyDB('./config/db.json')

exchangeDB = db.table('exchange')
#channelDb = db.table('channel')
#tradesDb = db.table('trades')
q = Query()

exchangeDB.insert({
    "name": CCXT_id1_name,
    "api": CCXT_id1_api,
    "secret": CCXT_id1_secret,
    "password": CCXT_id1_password
    })

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== exchange setup  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# EXCHANGE setup from variable id

if (not CCXT_id1_name):
    logger.info(msg=f"exchange is setup")
else:
    try:
        CCXT_ex = f'{CCXT_id1_name}'
        exchange_class = getattr(ccxt, CCXT_ex)
        exchange = exchange_class({
            'apiKey': CCXT_id1_api,
            'secret': CCXT_id1_secret,
            'options':  {
                'defaultType': CCXT_id1_defaulttype,
                        },
                    })
        m_ordertype = CCXT_id1_ordertype.upper()
        print (f"setup done for {exchange.name}")
        if (CCXT_test_mode=="True"):
         logger.info(msg=f"sandbox activated")
    
        else:
         logger.info(msg=f"no sandbox, setting up prod exchange")
    except:
        error_handler()
 
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##= telegram bot commands and messages==
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

trading=True #trading switch command

##list of commands 
commandlist= '/help /bal /trading'

####messages
menu=f'{TTVersion} \n {commandlist}'
exchangeinfo= f'Exchange: {exchange.name}  Sandbox: {CCXT_test_mode}'
unknown_command=f" {commandlist}"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## ========== startup message   ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def post_init(application: Application):
    logger.info(msg=f"bot is online")
    await application.bot.send_message(TG_CHANNEL_ID, f"Bot is online\n{menu}\n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== help  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when /help is used.  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.effective_chat.send_message(f"{menu} \n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##========== view balance  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#Send a message when /bal is used.
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    try:
        balance = exchange.fetch_free_balance()
        balance2 = {k: v for k, v in balance.items() if v>0}
        logger.info(msg=f"{balance2}")
        prettybal=""
        for iterator in balance2:
            logger.info(msg=f"{iterator}: {balance2[iterator]}")
            prettybal += (f"{iterator} : {balance2[iterator]} \n")
        await update.effective_chat.send_message(f"🏦 Balance \n{prettybal}")
    except ccxt.NetworkError as e:
        logger.error(msg=f"Failed due to a network error {e}")
        await update.effective_chat.send_message(f"⚠️{e}")
    except ccxt.ExchangeError as e:
        logger.error(msg=f"Failed due to a exchange error: {e}")
        await update.effective_chat.send_message(f"⚠️{e}")
    except Exception as e:
        logger.error(msg=f"Failed due to a CCXT error: {e}")
        await update.effective_chat.send_message(f"⚠️{e}") 

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##===== order parsing and placing  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## process buy or sell order 

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messagetxt = update.effective_message.text
    logger.info(msg=f"{messagetxt}")
    messagetxt_upper =messagetxt.upper()
    logger.info(msg=f"{messagetxt_upper}")
    filter_lst = ['BUY', 'SELL']
    if [ele for ele in filter_lst if(ele in messagetxt_upper)]:
        if (trading==False):
            await update.effective_chat.send_message("TRADING IS DISABLED")
        else:  # order format identified "sell BTCUSDT sl=6000 tp=4500 q=1%""
            try:
                #await update.message.reply_text("THIS IS AN ORDER TO PROCESS")
                order_m = Convert(messagetxt_upper) 
                m_dir= order_m[0]
                m_symbol=order_m[1]
                m_sl=order_m[2][3:7]
                m_tp=order_m[3][3:7]
                m_q=order_m[4][2:-1]
                logger.info(msg=f"Processing order: {m_symbol} {m_ordertype} {m_dir} {m_sl} {m_tp} {m_q}")
                #calculate percentage 
                m_price = float(exchange.fetchTicker(f'{m_symbol}').get('last'))
                totalusdtbal = exchange.fetchBalance()['USDT']['free']
                amountpercent=((totalusdtbal)*(float(m_q)/100))/float(m_price) 
                res = exchange.create_order(m_symbol, m_ordertype, m_dir, amountpercent)
                orderid=res['id']
                timestamp=res['datetime']
                symbol=res['symbol']
                side=res['side']
                amount=res['amount']
                price=res['price']
                await update.effective_chat.send_message(f"🟢 ORDER Processed: \n order id {orderid} @ {timestamp} \n  {side} {symbol} {amount} @ {price}")
                return orderid
            except ccxt.NetworkError as e:
                logger.error(msg=f"Failed due to a network error {e}")
                await update.effective_chat.send_message(f"⚠️{e}")
            except ccxt.ExchangeError as e:
                logger.error(msg=f"Failed due to a exchange error: {e}")
                await update.effective_chat.send_message(f"⚠️{e}")
            except Exception as e:
                logger.error(msg=f"Failed due to a CCXT error: {e}")
                await update.effective_chat.send_message(f"⚠️{e}") 
    else: error_handler()

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======= view last closed orders  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when /order is used.
async def lastorder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("lastorder_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view positions  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the /pos is used.
async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("position_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view today's pnl =========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when /profit or add the output to /bal

async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 print("pnl_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== trading switch  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when /trading is used

async def trading_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trading
    if (trading==False):
        trading=True
        await update.effective_chat.send_message(f"Trading is {trading}")
    else:
        trading=False
        await update.effective_chat.send_message(f"Trading is {trading}")
        

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##============ cex switch  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when /switch is used

async def cex_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  newexchange  = update.effective_message.text
  rows = db.all()
  if not rows:
   response = 'No data.'
  else:
   #logger.info(msg=f" {rows}")
   #response = 'Stored Exchanges:'
   for row in rows:
    response = row['name']
  #print(f"{response}")
  await update.effective_chat.send_message(f" new active exchange is {newexchange}")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== DB COMMAND ===============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

##=========  drop DB ========

async def dropDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"db table dropped")
    db.drop_tables()

##=========  show DB ========
async def showDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"display db")
    await update.effective_chat.send_message(f" db extract: \n {db.table('exchange').all()}")
    #return TinyDB('db.json')

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========  bot restart  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"bot is restarting")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=======  bot unknow command  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.error(update, 'unknown_command')

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========  bot error handling ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Log Errors caused by Updates

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:4000]
    errormessage=f"⚠️ Error encountered {tb_trim}"
    logger.error(msg=f"{errormessage}")
    #await context.bot.send_message(chat_id=, text=errormessage, parse_mode=ParseMode.HTML)
    await update.effective_chat.send_message(f"⚠️ Error encountered {tb_trim}")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== BOT  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

def main():
    """Start the bot."""
    # Create the Application
    try:
     application = Application.builder().token(TG_TOKEN).post_init(post_init).build()

    # Menus
     application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
     application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
     application.add_handler(MessageHandler(filters.Regex('/trading'), trading_switch))
     application.add_handler(MessageHandler(filters.Regex('/lastorder'), lastorder_command))
     application.add_handler(MessageHandler(filters.Regex('/position'), position_command))
     application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
     application.add_handler(MessageHandler(filters.Regex('/restart'), restart_command))
     application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))
     application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
     application.add_handler(MessageHandler(filters.Regex('/switch'), cex_switch))

# Message monitoring for order
     #application.add_handler(MessageHandler(filters.ALL, monitor))
     application.add_error_handler(error_handler)

#Run the bot
     application.run_polling()

    except Exception as error:
     logger.fatal("Bot failed to start. Error: " + str(error))
        

if __name__ == '__main__':
    main()



