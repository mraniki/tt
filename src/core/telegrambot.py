import asyncio
import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Update, CommandHandler, CallbackQueryHandler, \
#     ConversationHandler, MessageHandler, BaseFilter, run_async, Filters

# from core.tradeexecutor import TradeExecutor
# from util import formatter

TRADE_SELECT = "trade_select"
SHORT_TRADE = "short_trade"
LONG_TRADE = "long_trade"
OPEN_ORDERS = "open_orders"
FREE_BALANCE = "free_balance"

CANCEL_ORD = "cancel_order"
PROCESS_ORD_CANCEL = "process_ord_cancel"

COIN_NAME = "coin_name"
PERCENT_CHANGE = "percent_select"
AMOUNT = "amount"
PRICE = "price"
PROCESS_TRADE = "process_trade"

CONFIRM = "confirm"
CANCEL = "cancel"
END_CONVERSATION = ConversationHandler.END

class TelegramBot:
    def __init__(self, token: str):
        Application.builder().token(token).build()
        self._prepare()
        # on different commands - answer in Telegram
        self.add_handler(CommandHandler("start", start))
        self.add_handler(CommandHandler("bal", bal_command))
        self.add_handler(CommandHandler("help", help_command))

        # on non command i.e message - echo the message on Telegram
        self.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    def _prepare(self):

        # Create our handlers

       # def show_help(bot, update):
        #    update.effective_message.reply_text('Type /trade to show options')
        
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
            balance = self.exchange.free_balance
            #msg = f"Your available balance:\n{formatter.format_balance(balance)}"
            msg = f"Your available balance:\n{(balance)}"
            await update.message.reply_text(msg)

    def start_bot(self):
        self.run_polling()

    # @run_async
    # def _execute_trade(self, trade):
    #     loop = asyncio.new_event_loop()
    #     task = loop.create_task(self.trade_executor.execute_trade(trade))
    #     loop.run_until_complete(task)

    # @staticmethod
    # def build_trade(user_data):
    #     current_trade = user_data[TRADE_SELECT]
    #     price = user_data[PRICE]
    #     coin_name = user_data[COIN_NAME]
    #     amount = user_data[AMOUNT]
    #     percent_change = user_data[PERCENT_CHANGE]

    #     if current_trade == LONG_TRADE:
    #         return LongTrade(price, coin_name, amount, percent_change)
    #     elif current_trade == SHORT_TRADE:
    #         return ShortTrade(price, coin_name, amount, percent_change)
    #     else:
    #         raise NotImplementedError
