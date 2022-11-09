##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.9"

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
import asyncio
from telegram import Update    
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

#webhook
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

#ccxt
import ccxt
import json

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
TG_USER_ID = os.getenv("TG_USER_ID")
WBHKURL= os.getenv("WBHKURL")
URL=WBHKURL+TG_TOKEN

CCXT_id1_name = os.getenv("EXCHANGE1_NAME")
CCXT_id1_api = os.getenv("EXCHANGE1_YOUR_API_KEY")  
CCXT_id1_secret = os.getenv("EXCHANGE1_YOUR_SECRET") 
CCXT_id1_password = os.getenv("EXCHANGE1_YOUR_PASSWORD") 
CCXT_id1_ordertype = os.getenv("EXCHANGE1_ORDERTYPE")
CCXT_id1_defaulttype = os.getenv("EXCHANGE1_DEFAULTTYPE")

#CCXT SANDBOX details
CCXT_test_mode = os.getenv("TEST_SANDBOX_MODE")
CCXT_test_name = os.getenv("TEST_SANDBOX_EXCHANGE_NAME")  
CCXT_test_api = os.getenv("TEST_SANDBOX_YOUR_API_KEY") 
CCXT_test_secret = os.getenv("TEST_SANDBOX_YOUR_SECRET") 
CCXT_test_ordertype = os.getenv("TEST_SANDBOX_ORDERTYPE")
CCXT_test_defaulttype = os.getenv("TEST_SANDBOX_DEFAULTTYPE")
PORT = int(os.environ.get('PORT', '8443'))


if (TG_TOKEN==""):
    logger.info(msg=f"missing telegram token, Read the install instruction")
    sys.exit()
elif (CCXT_id1_name==""):
    logger.info(msg=f"missing main exchangeinfo, Read the install instruction")
    sys.exit()
elif (CCXT_id1_name==""):
    logger.info(msg=f"no sandbox setup")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== exchange setup  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# Enable logging and version check
#EXCHANGE1 from variable id

if (CCXT_test_mode=="True"):
    logger.info(msg=f"sandbox activated")
    try:
     CCXT_ex = f'{CCXT_test_name}'
     exchange_class = getattr(ccxt, CCXT_ex)
     exchange = exchange_class({
        'apiKey': CCXT_test_api,
        'secret': CCXT_test_secret
        })
     m_ordertype = CCXT_test_ordertype.upper()
     exchange.set_sandbox_mode(CCXT_test_mode)
     logger.info(msg=f"exchange setup done for {exchange.name} sandbox")
    except:
        error_handler()

else:
    logger.info(msg=f"no sandbox, setting up production exchange")
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
        m_ordertype = CCXT_test_ordertype.upper()
        print (f"exchange setup done for {exchange.name}")
    except:
        error_handler()

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##= telegram bot commands and messages==
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

trading=True #trading switch command

user_id = TG_USER_ID
##list of commands 
command1=['help']
command2=['bal']
command3=['trading']
command4=['lastorder']
command5=['position']
command6=['restart']
listofcommand = list(itertools.chain(command1, command2, command3))
commandlist= ' /'.join([str(elem) for elem in listofcommand])

####messages
menu=f'{TTVersion} \n /{commandlist}'
exchangeinfo= f'Exchange: {exchange.name}  Sandbox: {CCXT_test_mode}'
unknown_command=f" {commandlist}"

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## ========== startup message   ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

async def post_init(application: Application):
    logger.info(msg=f"bot is online")
    await application.bot.send_message(user_id, f"Bot is online\n{menu}\n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== help  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when the command /help is issued."""  
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.effective_chat.send_message(f"{menu} \n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##========== view balance  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#Send a message when the command /bal is issued.
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    try:
        balance = exchange.fetch_free_balance()
        balance2 = {k: v for k, v in balance.items() if v>0}
        # for key, value in balance.items():
        #     if value <= 0:
        #         del balance[key]
         # For convenience
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
## Send a message when an order 
## is identified

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
## Send a message when the command /order is issued.
async def lastorder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("lastorder_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view positions  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the command /position is issued.
async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("position_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view today's pnl =========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the command /profit or add the output to /bal

async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
 print("pnl_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== trading switch  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when the command /trading is issued
async def trading_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trading
    if (trading==False):
        trading=True
        await update.effective_chat.send_message(f"Trading is {trading}")
    else:
        trading=False
        await update.effective_chat.send_message(f"Trading is {trading}")
        
        
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
    # Create the Application and pass it your bot's token.
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


# Message monitoring for order
     #application.add_handler(MessageHandler(filters.ALL, monitor))
     application.add_error_handler(error_handler)

#Run the bot until the user presses Ctrl-C
     #application.run_polling()

# add handlers
     await application.bot.set_webhook(url=f"{URL}/telegram")

     # Set up webserver

     async def telegram(request: Request) -> Response:
     """Handle incoming Telegram updates by putting them into the `update_queue`"""
      await application.update_queue.put(
      Update.de_json(data=await request.json(), bot=application.bot)
     )
     return Response()

     # application.run_webhook(
     #    listen="0.0.0.0", 
     #    port=PORT, 
     #    url_path=TG_TOKEN,
     #    webhook_url=URL)
     async with application:
         await application.start()
         await webserver.serve()
         await application.stop()

    except Exception as error:
     logger.fatal("Bot failed to start. Error: " + str(error))
        
    # Run application and webserver together


     
if __name__ == '__main__':
    asyncio.run(main())



