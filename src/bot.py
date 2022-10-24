## IMPORT 
import logging
import sys
import os
import argparse
from dotenv import load_dotenv
from os import getenv
from pathlib import Path


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


import ccxt
from core.exchange import CryptoExchange
from core.tradeexecutor import TradeExecutor

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


#IMPORT ENV FILE 
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

# ENV VAR
telegram_tkn = os.getenv("TOKEN")
ALLOWED_USER_ID = getenv("ALLOWED_USER_ID")
parser = argparse.ArgumentParser(description="INT Transformation")
parser.add_argument("--user-id", required=False, type=int, default=ALLOWED_USER_ID)
args = parser.parse_args()
user_id = args.user_id
print(user_id)

print('python', sys.version)
print('CCXT Version:', ccxt.__version__)
print('Please wait while the program is loading...')

if not user_id:
    logger.warning('user_id not set, you will not be able to control the bot')

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

# Define a few command handlers. These usually take the two arguments update and
# context.

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Hi {user.mention_html()}!",
#         reply_markup=ForceReply(selective=True),
#     )


# def restart_handler(update, context):
#     username = update.message.from_user.username
#     cmd = context.args

#     print(f'[magenta]{ctime()}[/magenta] [bold cyan]{username}[/bold cyan]: [color(231)]/restart {" ".join(cmd)}[/color(231)]')

#     if username not in admins and username not in owners:
#         auto_retry(lambda: update.message.reply_text("<b>⚠️ Only bot admins are allowed to do that.</b>", parse_mode="html"))
#         print(f"[bold cyan]{username}[/bold cyan]: [yellow]⚠️ WARNING: [color(231)]/update[/color(231)] is not allowed.[/yellow]")
#         return

#     auto_retry(lambda: update.message.reply_text("Restarting...", parse_mode="html"))

#     git_output = subprocess.run(["git", "pull"],
#         capture_output=True,
#         encoding="utf-8"
#     ).stdout.strip()

#     poetry_output = subprocess.run(
#         ["/home/pcroland/.local/bin/poetry", "install", "--no-dev", "--remove-untracked"],
#         capture_output=True,
#         encoding="utf-8"
#     ).stdout.strip()

#     if str(update.message.chat_id) == config["main_chat_id"]:
#         update_message = f'{git_output}\n\n{poetry_output}'
#         update_message = f"<pre>{html.escape(update_message)}</pre>"
#         if len(update_message) > 1024:
#             update_message = f"{update_message[:1015]}...</pre>"
#         auto_retry(lambda: update.message.reply_text(update_message, parse_mode="html"))

#     with open("restart_id.txt", "w", encoding="utf-8") as fl:
#         fl.write(str(update.message.chat_id))

#     os.execv(sys.argv[0], sys.argv)

#     if os.path.exists(restart_id_path):
#         with open("restart_id.txt", "r", encoding="utf-8") as fl:
#             restart_id = fl.read()
#     else:
#         restart_id = config["main_chat_id"]


async def post_init(application: Application):
    await application.bot.send_message(user_id, "Bot is online")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    txt = update.message.text
    txt.capitalize()
    target1 = "BUY"
    target2 = "SELL"

    if txt.__contains__(target1) or txt.__contains__(target2):
      await update.message.reply_text("THIS IS AN ORDER TO PROCESS")
      print ("processing order")
    # elif update.message.text.__contains__(target2):
    #   await update.message.reply_text("THIS IS A SELL ORDER TO PROCESS")
    else: help_command



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)



#BOT
def main():
    """Start the bot."""
    #ex1 setup
    exchange1 = CryptoExchange(ccxt_ex_1)
    balance1 = exchange1.free_balance
    print (balance1)
    print ("ex1 setup done")
    trade_executor = TradeExecutor(exchange1)

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_tkn).post_init(post_init).build()
    application.add_handler(CommandHandler(["start","help"], help_command))
    # application.add_handler(MessageHandler(filters.CHAT, monitor))
    application.add_handler(MessageHandler(filters.ALL, monitor))



    # Run the bot until the user presses Ctrl-C
    
    application.run_polling()



if __name__ == '__main__':
    main()
