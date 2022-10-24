import asyncio
import logging

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


class TelegramBot:
    def __init__(self, token: str):
        Application.builder().token(token).build()
        self._prepare()
        # on different commands - answer in Telegram

    def _prepare(self):
        
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

        def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE)-> None:
            try:
                raise context.error
            except TelegramError as e:
                update.message.reply_text(str(e))
                logger.exception(e)
            except Exception as e:
                update.message.reply_text(str(e))
                logger.exception(e)
                # Create our handlers

        self.add_handler(CommandHandler("start", start))
        self.add_handler(CommandHandler("bal", bal_command))
        self.add_handler(CommandHandler("help", help_command))

    def start_bot(self):
        self.run_polling()


