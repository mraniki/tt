## IMPORT 
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

# Enable logging and version check
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
TTVersion=0.6

print('TT', TTVersion)
print('python', sys.version)
print('CCXT Version:', ccxt.__version__)
print('Please wait while the program is loading...')


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

exchange_id1 = getenv("EXCHANGE1")
exchange_id1_api = getenv("EXCHANGE1YOUR_API_KEY")  
exchange_id1_secret = getenv("EXCHANGE1YOUR_SECRET") 




#EXCHANGE1 from variable id
exchange_id = exchange_id1
exchange_class = getattr(ccxt, exchange_id)
ccxt_ex_1 = exchange_class({
    'apiKey': exchange_id1_api,
    'secret': exchange_id1_secret,
})


def Convert(string):
   li = list(string.split(" "))
   return li

def log(severity, msg):
   logger.log(severity, msg)


#ex1 setup
exchange1 = CryptoExchange(ccxt_ex_1)
print ("ex1 setup done")

##list of commands 
command1=['help']
command2=['bal']
command3=['order']
command4=['trading']
listofcommand = list(itertools.chain(command1, command2, command3, command4))
commandlist= ' /'.join([str(elem) for elem in listofcommand])
trading=True 

async def post_init(application: Application):
    await application.bot.send_message(user_id, f"Bot is online Version {TTVersion} \n /{commandlist} ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f"Use /{commandlist}")

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
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
         if res["error"]:
            await update.message.reply_text(f"{res}")
         else: 
            await update.message.reply_text(f"ORDER PLACED SUCCESSFULLY {res}")
            return res
    else: error_handler

async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    balance1 = exchange1.free_balance
    print (balance1)
    balancetodisplay=json.dumps(balance1, sort_keys=True, indent=4)
    await update.message.reply_text(f"balance {balance1} OR {balancetodisplay}")

async def orderlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    openorder1 = exchange1.fetch_open_orders("BTC/USDT")
    await update.message.reply_text(f" list of orders {openorder1}")    

async def trading_activation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    global trading
    if (trading==False):
      trading=True
      await update.message.reply_text(f"Trading is {trading}")
    else:
      trading=False
      await update.message.reply_text(f"Trading is {trading}")

def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    

#BOT
def main():

    # trade_executor = TradeExecutor(exchange1)

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_tkn).post_init(post_init).build()

    # Menus
    application.add_handler(CommandHandler(command1, help_command))
    application.add_handler(CommandHandler(command2, bal_command))
    application.add_handler(CommandHandler(command3, orderlist_command))
    application.add_handler(CommandHandler(command4, trading_activation))
    # Message monitoring for order
    application.add_handler(MessageHandler(filters.ALL, monitor))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
