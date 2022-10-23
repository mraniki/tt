import logging
import sys

import os
import argparse
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
#from core.telegrambot import TelegramBot

import ccxt
from core.exchange import CryptoExchange

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

print('python', sys.version)
print('CCXT Version:', ccxt.__version__)
print('Please wait while the program is loading...')


# VAR
telegram_tkn = os.getenv("TOKEN")
ALLOWED_USER_ID = getenv("ALLOWED_USER_ID")
parser = argparse.ArgumentParser(description="INT Transformation")
parser.add_argument("--user-id", required=False, type=int, default=ALLOWED_USER_ID)
args = parser.parse_args()
user_id = args.user_id

if not user_id:
    logger.warning('user_id not set, you will not be able to control the bot')

exchange_id1 = getenv("EXCHANGE1")
exchange_id1_api = getenv("EXCHANGE1YOUR_API_KEY")  
exchange_id1_secret = getenv("EXCHANGE1YOUR_SECRET") 




#BOT





def main() -> None:
    #"Start the bot."
    # Create the Application and pass it your bot's token.
 
    application = Application.builder().token(telegram_tkn).build()
    #telegram_bot.start_bot()

    #EXCHANGE
    # from variable id
    exchange_id = exchange_id1
    exchange_class = getattr(ccxt, exchange_id)
    ccxt_ex_1 = exchange_class({
        'apiKey': exchange_id1_api,
        'secret': exchange_id1_secret,
    })
    exchange1 = CryptoExchange(ccxt_ex_1)

    balance1 = exchange1.free_balance
    print (balance1)
    #balancee1 = exchange1.balance
    #print (balancee1)



    #update.message.reply_text("Bot started")

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bal", bal_command))
    application.add_handler(CommandHandler("position", position_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hello", hello))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()



if __name__ == "__main__":
 main()



# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /bal is issued."""
    await update.message.reply_text(balance1)

async def position_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /position is issued."""
    await update.message.reply_text(balancee1)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello I'm online")