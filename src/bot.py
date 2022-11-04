##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=============== VERSION  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

TTVersion="🪙TT 0.7.3"

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
    except NameError:
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
    except NameError:
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
listofcommand = list(itertools.chain(command1, command2, command3, command4, command5))
commandlist= ' /'.join([str(elem) for elem in listofcommand])

####messages
menu=f'{TTVersion} \n /{commandlist}'
exchangeinfo= f'Exchange: {exchange.name}  Sandbox: {CCXT_test_mode}'

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

    await update.message.reply_text(f"{menu} \n {exchangeinfo} ")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##========== view balance  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
#Send a message when the command /bal is issued.
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    try:
        balance = exchange.fetch_free_balance()
        for key, value in balance.items():
            if value < 0:
                del balance[key]
            elif isinstance(value, dict):
                del_none(value)
         # For convenience
        logger.info(msg=f"{balance}")
        prettybal=""
        for iterator in balance:
            logger.info(msg=f"{iterator}: {balance[iterator]}")
            prettybal += (f"{iterator} : {balance[iterator]} \n")
        await update.message.reply_text(f"🏦 Balance \n{prettybal}")
    except ccxt.NetworkError as e:
        logger.error(msg=f"Failed due to a network error {e}")
        await update.message.reply_text(f"⚠️{e}")
    except ccxt.ExchangeError as e:
        logger.error(msg=f"Failed due to a exchange error: {e}")
        await update.message.reply_text(f"⚠️{e}")
    except Exception as e:
        logger.error(msg=f"Failed due to a CCXT error: {e}")
        await update.message.reply_text(f"⚠️{e}") 


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##===== order parsing and placing  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when an order 
## is identified

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messagetxt = update.message.text
    print(messagetxt)
    messagetxt_upper =messagetxt.upper()
    print(messagetxt_upper)
    filter_lst = ['BUY', 'SELL']
    if [ele for ele in filter_lst if(ele in messagetxt_upper)]:
        if (trading==False):
            await update.message.reply_text("TRADING IS DISABLED")
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
                await update.message.reply_text(f"🟢 ORDER Processed: \n order id {orderid} @ {timestamp} \n  {side} {symbol} {amount} @ {price}")
                return orderid
            except ccxt.NetworkError as e:
                logger.error(msg=f"Failed due to a network error {e}")
                await update.message.reply_text(f"⚠️{e}")
            except ccxt.ExchangeError as e:
                logger.error(msg=f"Failed due to a exchange error: {e}")
                await update.message.reply_text(f"⚠️{e}")
            except Exception as e:
                logger.error(msg=f"Failed due to a CCXT error: {e}")
                await update.message.reply_text(f"⚠️{e}") 
    else: error_handler()

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======= view last closed orders  =====
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the command /order is issued.
async def lastorder_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("orderlist_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view positions  ========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the command /position is issued.
async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("orderlist_command")

##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##=========== view today's pnl =========
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
## Send a message when the command /profit or add the output to /bal


##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##======== trading switch  =============
##▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
##Send a message when the command /trading is issued
async def trading_switch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
## Log Errors caused by Updates

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:4000]
    await update.message.reply_text(f"⚠️ Error encountered {tb_trim}")


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
    application.add_handler(CommandHandler(command3, trading_switch))
    application.add_handler(CommandHandler(command4, lastorder_command))
    application.add_handler(CommandHandler(command5, position_command))
    # Message monitoring for order
    application.add_handler(MessageHandler(filters.ALL, monitor))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()



