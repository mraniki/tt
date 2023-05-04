"""
TalkyTrader 🪙🗿
"""
__version__ = "1.4.2"

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI

import ccxt
from dxsp import DexSwap
from findmyorder import FindMyOrder

import apprise
from apprise import NotifyFormat
from telethon import TelegramClient, events
import discord
import simplematrixbotlib as botlib

from config import settings, logger


async def parse_message(msg):
    """main parser"""
    logger.info("message received %s", msg)

    try:
        # Initialize response
        response = None
        # Initialize FindMyOrder object
        fmo = FindMyOrder()

        # Check if message starts with word to ignore
        if msg.startswith(settings.bot_ignore):
            return

        # Check if message starts with bot prefix
        if msg.startswith(settings.bot_prefix):
            command = msg[1:]
            # Check if command is help command
            if command == settings.bot_command_help:
                response = await help_command()
            # Check if command is trading command
            elif command == settings.bot_command_trading:
                response = await trading_switch_command()
            # Check if command is balance command
            elif command == settings.bot_command_bal:
                response = await account_balance_command()
            # Check if command is position command
            elif command == settings.bot_command_pos:
                response = await account_position_command()
            # Check if command is restart command
            elif command == settings.bot_command_restart:
                response = await restart_command()
            # Check if command is invalid
            else:
                logger.warning("invalid command: %s", command)
                return
        # Check if message contains an order
        if bot_trading_switch is False:
            return
        if await fmo.search(msg):
            # Order found
            order = await fmo.get_order(msg)
            logger.info("order: %s", order)
            response = await execute_order(order)

        # Check if response is valid
        if response:
            await notify(response)

    except Exception as e:
        logger.error("Error while parsing message: %s", e)


async def notify(msg):
    """💬 MESSAGING to user"""
    if not msg:
        return
    apobj = apprise.Apprise()
    if settings.discord_webhook_id:
        url = (f"discord://{str(settings.discord_webhook_id)}/"
               f"{str(settings.discord_webhook_token)}")
    elif settings.matrix_hostname:
        url = (f"matrixs://{settings.matrix_user}:{settings.matrix_pass}@"
               f"{settings.matrix_hostname[8:]}:443/"
               f"{str(settings.bot_channel_id)}")
    else:
        url = (f"tgram://{str(settings.bot_token)}/"
               f"{str(settings.bot_channel_id)}")
    try:
        apobj.add(url)
        await apobj.async_notify(body=msg, body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.error("%s not sent: %s", msg, e)


async def load_exchange():
    """load_exchange."""
    logger.info("Setting up exchange")
    global exchange
    global bot_trading_switch
    bot_trading_switch = True
    if settings.cex_api:
        client = getattr(ccxt, settings.cex_name)
        try:
            if settings.cex_defaulttype != "SPOT":
                exchange = client({
                        'apiKey': settings.cex_api,
                        'secret': settings.cex_secret,
                        'options': {
                                'defaultType': settings.cex_defaulttype,
                                    },
                        }
                    )
            else:
                exchange = client({
                        'apiKey': settings.cex_api,
                        'secret': settings.cex_secret,
                        })
            if settings.cex_testmode == 'True':
                logger.info("sandbox setup")
                exchange.set_sandbox_mode('enabled')
            # markets = exchange.load_markets()
            logger.debug("CEXcreated: %s", exchange)
        except Exception as e:
            logger.warning("load_exchange: %s", e)

    elif settings.dex_chain_id:
        chain_id = settings.dex_chain_id
        wallet_address = settings.dex_wallet_address
        private_key = settings.dex_private_key
        block_explorer_api = settings.dex_block_explorer_api

        try:
            exchange = DexSwap(
                chain_id=chain_id,
                wallet_address=wallet_address,
                private_key=private_key,
                block_explorer_api=block_explorer_api
                )
            logger.info("DEX created %s on chain %s",
                        exchange,
                        exchange.chain_id
                        )
        except Exception as e:
            logger.warning("load_exchange: %s", e)
    else:
        logger.error("no CEX/DEX config")
        return


async def execute_order(order_params):
    """execute_order."""
    if order_params is None:
        logger.warning("execute_order: No order params provided")
        await notify("⚠️ No order params provided")
        return
    action = order_params.get('action')
    instrument = order_params.get('instrument')
    stop_loss = order_params.get('stop_loss', 1000)
    take_profit = order_params.get('take_profit', 1000)
    quantity = order_params.get('quantity', 1)
    try:
        order_confirmation = (f"⬇️ {instrument}" if (action == "SELL")
                              else f"⬆️ {instrument}\n")
        if "DexSwap" in str(type(exchange)):
            order = await exchange.execute_order(
                                action=action,
                                instrument=instrument,
                                stop_loss=int(stop_loss),
                                take_profit=int(take_profit),
                                quantity=int(quantity)
                                )
            order_confirmation += order['confirmation']
        else:
            if await get_account_balance() == "No Balance":
                await notify("⚠️ Check your Balance")
                return
            asset_out_quote = float(exchange.fetchTicker(f'{instrument}')
                                    .get('last'))
            asset_out_balance = await get_quote_ccy_balance()
            if not asset_out_balance:
                return
            transaction_amount = ((asset_out_balance)*(float(quantity)/100)
                                  / asset_out_quote)
            order = exchange.create_order(
                                instrument,
                                settings.cex_ordertype,
                                action,
                                transaction_amount
                                )
            order_confirmation += f"➕ Size: {order['amount']}\n\
                                    ⚫️ Entry: {order['price']}\n\
                                    ℹ️ {order['id']}\n\
                                    🗓️ {order['datetime']}"
        return order_confirmation

    except Exception as e:
        logger.warning("execute_order: %s", e)
        await notify(f"⚠️ order execution error: {e}")
        return


async def get_account_balance():
    """return account balance."""
    balance = "🏦 Balance\n"
    try:
        if "DexSwap" in str(type(exchange)):
            balance += await exchange.get_account_balance()
        else:
            raw_balance = exchange.fetch_free_balance()
            filtered_balance = {k: v for k, v in
                                raw_balance.items()
                                if v is not None and v > 0}
            balance += "".join(f"{iterator}: {value} \n" for
                               iterator, value in
                               filtered_balance.items())
            if not balance:
                balance += "No Balance"
        return balance
    except Exception as e:
        logger.warning("get_account_balance: %s", e)


async def get_quote_ccy_balance():
    """return main instrument balance."""
    try:
        return (
            await exchange.get_quote_ccy_balance()
            if "DexSwap" in str(type(exchange))
            else exchange.fetchBalance()[f"{settings.trading_quote_ccy}"][
                "free"
            ]
        )
    except Exception as e:
        logger.warning("get_quote_ccy_balance: %s", e)
        await notify(f"⚠️ Check balance {settings.trading_quote_ccy}")


async def get_account_position():
    """return account position."""
    try:
        position = "📊 Position\n"
        if "DexSwap" in str(type(exchange)):
            open_positions = await exchange.get_account_position()
        else:
            open_positions = exchange.fetch_positions()
            open_positions = [p for p in open_positions if p['type'] == 'open']
        position += open_positions
        return position
    except Exception as e:
        logger.warning("get_account_position: %s", e)


async def get_account_margin():
    try:
        return
    except Exception as e:
        logger.warning("get_account_margin: %s", e)


# 🦾BOT ACTIONS


async def post_init():
    # Notify the user of the bot's online status
    logger.info("Bot is online %s", __version__)
    await notify(f"Bot is online {__version__}")


async def help_command():
    # Notify the user of help message
    help_message = """
    🏦<code>/bal</code>
    📦<code>buy BTCUSDT sl=1000 tp=20 q=1%</code>
    🔀 <code>/trading</code>"""
    if settings.discord_webhook_id:
        help_message = help_message.replace("<code>", "`")
        help_message = help_message.replace("</code>", "`")
    bot_menu_help = f"{__version__}\n{help_message}"
    return f"{bot_menu_help}"


async def account_balance_command():
    # Return the account balance
    logger.info("account_bal_command")

    return await get_account_balance()


async def account_position_command():
    # Return the account position
    return await get_account_position()


async def trading_switch_command():
    # global variable to store the trading switch
    global bot_trading_switch
    # set the trading switch to the opposite of the current value
    bot_trading_switch = not bot_trading_switch
    # return a string with the trading switch status
    return f"Trading is now {'enabled' if bot_trading_switch else 'disabled'}."


async def restart_command():
    # Restart bot
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

# 🤖BOT


async def listener():
    """Launch Bot Listener"""
    try:
        await load_exchange()
        while True:
            if settings.discord_webhook_id:
                # DISCORD
                intents = discord.Intents.default()
                intents.message_content = True
                bot = discord.Bot(intents=intents)

                @bot.event
                async def on_ready():
                    await post_init()

                @bot.event
                async def on_message(message: discord.Message):
                    await parse_message(message.content)
                await bot.start(settings.bot_token)
            elif settings.matrix_hostname:
                # MATRIX
                config = botlib.Config()
                config.emoji_verify = True
                config.ignore_unverified_devices = True
                config.store_path = './config/matrix/'
                creds = botlib.Creds(
                            settings.matrix_hostname,
                            settings.matrix_user,
                            settings.matrix_pass
                            )
                bot = botlib.Bot(creds, config)

                @bot.listener.on_startup
                async def room_joined(room):
                    await post_init()

                @bot.listener.on_message_event
                async def on_matrix_message(room, message):
                    await parse_message(message.body)
                await bot.api.login()
                bot.api.async_client.callbacks = botlib.Callbacks(
                                                    bot.api.async_client, bot
                                                    )
                await bot.api.async_client.callbacks.setup_callbacks()
                for action in bot.listener._startup_registry:
                    for room_id in bot.api.async_client.rooms:
                        await action(room_id)
                await bot.api.async_client.sync_forever(
                                                        timeout=3000,
                                                        full_state=True
                                                    )
            elif settings.telethon_api_id:
                # TELEGRAM
                bot = await TelegramClient(
                            None,
                            settings.telethon_api_id,
                            settings.telethon_api_hash
                            ).start(bot_token=settings.bot_token)
                await post_init()

                @bot.on(events.NewMessage())
                async def telethon(event):
                    await parse_message(event.message.message)

                await bot.run_until_disconnected()
            else:
                logger.error("Check settings")
                await asyncio.sleep(7200)

    except Exception as e:
        logger.error("Bot not started: %s", e)


# ⛓️API
app = FastAPI(title="TALKYTRADER",)


@app.on_event("startup")
def startup_event():
    """fastapi startup"""
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(listener())
        logger.info("Webserver started")
    except Exception as e:
        loop.stop()
        logger.error("Bot start error: %s", e)


@app.on_event('shutdown')
async def shutdown_event():
    """fastapi shutdown"""
    global uvicorn
    logger.info("Webserver shutting down")
    uvicorn.keep_running = False


@app.get("/")
def root():
    """Fastapi root"""
    return {f"Bot is online {__version__}"}


@app.get("/health")
def health_check():
    """fastapi health"""
    logger.info("Healthcheck")
    return {f"Bot is online {__version__}"}


# 🙊TALKYTRADER


if __name__ == '__main__':
    """Launch Talky"""
    uvicorn.run(app, host=settings.host, port=settings.port)
