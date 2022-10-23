import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

import ccxt
import argparse
from os import getenv
import core.telegrambot 

message = 'Please wait while the program is loading...'
print(message)


# VAR
telegram_tkn = getenv("TOKEN")
ALLOWED_USER_ID = getenv("ALLOWED_USER_ID")
parser = argparse.ArgumentParser(description="INT Transformation")
parser.add_argument("--user-id", required=False, type=int, default=ALLOWED_USER_ID)
args = parser.parse_args()
user_id = args.user_id

if not user_id:
    logger.warning('user_id not set, you will not be able to control the bot')

exchange_id = getenv("EXCHANGE1")
exchange_id1_api = getenv("EXCHANGE1YOUR_API_KEY")  
exchange_id1_secret = getenv("EXCHANGE1YOUR_SECRET") 

#EXCHANGE
exchange_class = getattr(ccxt, exchange_id)
ccxt_ex = exchange_class({
    'apiKey': exchange_id1_api,
    'secret': exchange_id1_secret,
})



#BOT


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_tkn).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
 main()
