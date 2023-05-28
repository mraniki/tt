"""
TalkyTrader 🪙🗿
"""
__version__ = "1.7.10"

import os
import sys
import asyncio
import uvicorn
import socket
import ping3
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
    logger.info("message %s", msg)

    try:
        # Initialize FindMyOrder object
        fmo = FindMyOrder()

        # Check if message starts with word to ignore
        if msg.startswith(settings.bot_ignore):
            return
        # Check if message starts with bot prefix
        if msg.startswith(settings.bot_prefix):
            command = (msg.split(" ")[0])[1:]
            if command == settings.bot_command_help:
                await notify(settings.bot_msg_help)
            elif command == settings.bot_command_trading:
                await notify(await trading_switch_command())
            elif command == settings.bot_command_quote:
                symbol = msg.split(" ")[1]
                await notify(await get_quote(symbol))
            elif command == settings.bot_command_bal:
                await notify(await account_balance_command())
            elif command == settings.bot_command_pos:
                await notify(await account_position_command())
            elif command == settings.bot_command_restart:
                await restart_command()
            else:
                logger.warning("invalid command: %s", command)
            return

        # Order Process
        if settings.trading_active and await fmo.search(msg):
            # Order found
            order = await fmo.get_order(msg)
            order = await execute_order(order)
            if order:
                await notify(order)

    except Exception as e:
        logger.error("Error while parsing message: %s", e)


async def notify(msg):
    """💬 MESSAGING to user"""
    logger.debug("msg %s", msg)
    if not msg:
        return
    apobj = apprise.Apprise()
    if settings.discord_webhook_id:
        url = (f"discord://{str(settings.discord_webhook_id)}/"
               f"{str(settings.discord_webhook_token)}")
        if isinstance(msg, str):
            msg = msg.replace("<code>", "`")
            msg = msg.replace("</code>", "`")
    elif settings.matrix_hostname:
        url = (f"matrixs://{settings.matrix_user}:{settings.matrix_pass}@"
               f"{settings.matrix_hostname[8:]}:443/"
               f"{str(settings.bot_channel_id)}")
    else:
        url = (f"tgram://{str(settings.bot_token)}/"
               f"{str(settings.bot_channel_id)}")
    try:
        apobj.add(url)
        await apobj.async_notify(body=str(msg), body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.error("%s not sent: %s", msg, e)


def get_host_ip() -> str:
    """Returns the IP address of the host."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((settings.ping, 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        pass


def get_ping(host: str = settings.ping) -> float:
    """Returns  ping (in milliseconds)"""
    response_time = ping3.ping(host, unit='ms')
    return round(response_time, 3)


async def load_exchange():
    """load_exchange."""
    global exchange
    #global bot_trading_switch
    #bot_trading_switch = True
    try:
        if settings.cex_name != '':
            client = getattr(ccxt, settings.cex_name)
            exchange = client({
                'apiKey': settings.cex_api,
                'secret': settings.cex_secret,
                'password': (settings.cex_password or ''),
                'enableRateLimit': True,
                'options': {
                    'defaultType': settings.cex_defaulttype,
                            }})
            if settings.cex_testmode:
                exchange.set_sandbox_mode('enabled')
        elif settings.dex_chain_id != '':
            exchange = DexSwap()
    except Exception as e:
        logger.warning("exchange: %s", e)


async def execute_order(order_params):
    """execute_order."""
    if order_params is None:
        await notify("⚠️ Missing params")
        return
    action = order_params.get('action')
    instrument = order_params.get('instrument')
    quantity = order_params.get('quantity', settings.trading_risk_amount)
    try:
        if action is None or instrument is None:
            return
        trade_confirmation = (
            f"⬇️ {instrument}" if (action == "SELL")
            else f"⬆️ {instrument}\n")
        if isinstance(exchange, DexSwap):
            trade = await exchange.execute_order(order_params)
            if trade:
                trade_confirmation += trade['confirmation']
            else:
                return
        else:
            if await get_account_balance() == "No Balance":
                await notify("⚠️ Check Balance")
                return
            asset_out_quote = float(exchange.fetchTicker(f'{instrument}')
                                    .get('last'))
            asset_out_balance = await get_trading_asset_balance()
            if not asset_out_balance:
                return
            transaction_amount = ((asset_out_balance)*(float(quantity)/100)
                                  / asset_out_quote)
            if trade := exchange.create_order(
                instrument, settings.cex_ordertype, action, transaction_amount
            ):
                trade_confirmation += f"➕ Size: {round(trade['amount'],4)}\n"
                trade_confirmation += f"⚫️ Entry: {round(trade['price'],4)}\n"
                trade_confirmation += f"ℹ️ {trade['id']}\n"
                trade_confirmation += f"🗓️ {trade['datetime']}"
            else:
                return
        return trade_confirmation

    except Exception as e:
        logger.warning("execute_order: %s", e)
        await notify(f"⚠️ order execution: {e}")
        return


async def get_quote(symbol):
    """return quote"""
    try:
        if isinstance(exchange, DexSwap):
            return (await exchange.get_quote(symbol))
        else:
            return f"🏦 {await exchange.fetchTicker (symbol)}"
    except Exception as e:
        logger.warning("get_quote: %s", e)


async def get_account(exchange):
    """Return the account associated with the exchange."""
    try:
        return exchange.account if isinstance(exchange, DexSwap) else exchange.uid
    except Exception as e:
        logger.warning("Failed to get account: %s", e)


async def get_account_balance():
    """return account balance."""
    balance = "🏦 Balance\n"
    try:
        if isinstance(exchange, DexSwap):
            balance += str(await exchange.get_account_balance())
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


async def get_trading_asset_balance():
    """return main instrument balance."""
    try:
        if isinstance(exchange, DexSwap):
            return await exchange.get_trading_asset_balance()
        else:
            return exchange.fetchBalance()[f"{settings.trading_asset}"]["free"]
    except Exception as e:
        await notify(f"⚠️ Check balance {settings.trading_asset}")


async def get_account_position():
    """return account position."""
    try:
        position = "📊 Position\n"
        if isinstance(exchange, DexSwap):
            open_positions = await exchange.get_account_position()
        else:
            open_positions = exchange.fetch_positions()
            open_positions = [p for p in open_positions if p['type'] == 'open']
        position += open_positions
        position += await get_account_margin()
        return position
    except Exception as e:
        logger.warning("account_position: %s", e)


async def get_account_margin():
    try:
        margin = "\n🪙 margin\n"
        if isinstance(exchange, DexSwap):
            margin += 0
        else:
            margin += await exchange.fetch_balance({
                'type': 'margin',
                })
        return margin
    except Exception as e:
        logger.warning("account_margin: %s", e)


# 🦾BOT ACTIONS
async def init_message():
    version = __version__
    try:
        ip = get_host_ip()
        ping = get_ping()
        exchange_name = type(exchange).__name__
        account_info = await get_account(exchange)
        start_up = f"🗿 {version}\n🕸️ {ip}\n🏓 {ping}\n💱 {exchange_name}\n🪪 {account_info}"
    except Exception as e:
        logger.warning("init_message: %s", e)
        start_up = f"🗿 {version}\n"
    return start_up


async def post_init():
    # Notify of the bot's online status
    logger.info(await init_message())
    await notify(await init_message())


async def account_balance_command():
    # Return the account balance
    return await get_account_balance()


async def account_position_command():
    # Return the account position
    return await get_account_position()


async def trading_switch_command():
    settings.trading_active = not settings.trading_active
    return f"Trading is now {'enabled' if settings.trading_active else 'disabled'}."


async def restart_command():
    # Restart bot
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

# 🤖BOT


async def listener():
    """Launch Bot Listener"""
    try:
        await load_exchange()
    except Exception as e:
        logger.error("exchange not loaded: %s", e)
    try:
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
                logger.warning("Check bot settings")
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
async def root():
    """Fastapi root"""
    return await init_message()


@app.get("/health")
async def health_check():
    """fastapi health"""
    logger.info("Healthcheck")
    return await init_message()


# 🙊TALKYTRADER


if __name__ == '__main__':
    """Launch Talky"""
    uvicorn.run(app, host=settings.host, port=int(settings.port))
