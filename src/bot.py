"""
TalkyTrader 🪙🗿
"""
__version__ = "1.1.6"

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI

import pyparsing as pp
from pyparsing import one_of

import ccxt
from dxsp import DexSwap
from findmyorder import FindMyOrder

import apprise
from apprise import NotifyFormat
from telethon import TelegramClient, events
import discord
import simplematrixbotlib as botlib

from config import settings, logger

#🔁UTILS
async def parse_message(msg):
    """main parser"""
    logger.info("message received %s",msg)

    try:
        response = None
        fmo = FindMyOrder()

        # Check if message starts with bot prefix
        if msg.startswith(settings.bot_prefix):
            command = msg[1:]
            if command == settings.bot_command_help:
                response = await help_command()
            elif command == settings.bot_command_trading:
                response = await trading_switch_command()
            elif command == settings.bot_command_bal:
                response = await account_balance_command()
            elif command == settings.bot_command_pos:
                response = await account_position_command()
            elif command == settings.bot_command_restart:
                response = await restart_command()
            else:
                logger.warning("invalid command: %s", command)
                return
        # Check if message contains an order
        order = await fmo.get_order(msg)
        if order:
            logger.info("order: %s", order)
            response = await execute_order(
                            order['action'],
                            order["instrument"],
                            order["stop_loss"],
                            order["take_profit"],
                            order["quantity"]
                            )

        if response:
            await notify(response)

    except Exception as e:
        logger.error("Error while parsing message: %s", e)

async def notify(msg):
    """💬MESSAGING"""
    if not msg:
        return
    apobj = apprise.Apprise()
    if settings.discord_webhook_id:
        apobj.add(f'discord://{str(settings.discord_webhook_id)}/{str(settings.discord_webhook_token)}')
    elif settings.matrix_hostname:
        apobj.add(f"matrixs://{settings.matrix_user}:{settings.matrix_pass}@{settings.matrix_hostname[8:]}:443/{str(settings.bot_channel_id)}")
    else:
        apobj.add(f'tgram://{str(settings.bot_token)}/{str(settings.bot_channel_id)}')
    try:
        await apobj.async_notify(body=msg, body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.error("%s not sent: %s", msg, e)

async def notify_error(error_msg):
    """⚠️ notification to user"""
    msg = f"⚠️ {error_msg}"
    await notify(msg)

#💱EXCHANGE
async def load_exchange():
    """load_exchange."""
    logger.info("Setting up exchange")
    global exchange_type
    global exchange_name
    global cex
    global dex
    global bot_trading_switch
    global price_type
    bot_trading_switch = True
    if settings.cex_api:
        client = getattr(ccxt, settings.cex_name)
        try:
            if settings.cex_defaultype!="SPOT":
                cex = client({
                        'apiKey': settings.cex_api,
                        'secret': settings.cex_secret,
                        'options': {
                                'defaultType': settings.cex_defaultype,
                                    },
                        })
            else:
                cex = client({
                        'apiKey': settings.cex_api,
                        'secret': settings.cex_secret, 
                        })
            price_type = settings.cex_ordertype
            if settings.cex_testmode == 'True':
                logger.info("sandbox setup")
                cex.set_sandbox_mode('enabled')
                exchange_name = settings.cex_name
            markets = cex.load_markets()
            logger.debug("CEXcreated: %s", cex)
            exchange_type = 'cex'
        except Exception as e:
            logger.warning("load_exchange: %s", e)

    elif settings.dex_chain_id:
        chain_id = settings.dex_chain_id
        wallet_address = settings.dex_wallet_address
        private_key = settings.dex_private_key
        block_explorer_api = settings.dex_block_explorer_api

        try:
            dex = DexSwap(
                chain_id=chain_id,
                wallet_address=wallet_address,
                private_key=private_key,
                block_explorer_api=block_explorer_api
                )
            logger.info("DEX created %s on chain %s",
                        dex,
                        dex.chain_id
                        )
            exchange_type = 'dex'
            exchange_name = dex.router
        except Exception as e:
            logger.warning("load_exchange: %s", e)
    else:
        logger.error("no CEX/DEX config")
        return

#📦ORDER
async def execute_order(action,
                    instrument,
                    stop_loss=1000,
                    take_profit=1000,
                    quantity=1
                ):
    """execute_order."""
    if bot_trading_switch is False:
        return
    try:
        order_confirmation = f"⬇️ {instrument}" if (action=="SELL") else f"⬆️ {instrument}\n"
        if exchange_type == 'dex':
            order = await dex.execute_order(
                                action=action,
                                instrument=instrument,
                                stop_loss=stop_loss,
                                take_profit=take_profit,
                                quantity=quantity
                                )
            order_confirmation+= order['confirmation']
        else:
            if await get_account_balance()=="No Balance":
                await notify_error("Check your Balance")
                return
            asset_out_quote = float(cex.fetchTicker(f'{instrument}').get('last'))
            totalusdtbal = await get_base_trading_symbol_balance() ##cex.fetchBalance()['USDT']['free']
            amountpercent = (totalusdtbal)*(float(quantity)/100) / asset_out_quote
            order = cex.create_order(
                                instrument,
                                price_type,
                                action,
                                amountpercent
                                )
            order_confirmation+= f"➕ Size: {order['amount']}\n\
                                    ⚫️ Entry: {order['price']}\n\
                                    ℹ️ {order['id']}\n\
                                    🗓️ {order['datetime']}"
        return order_confirmation

    except Exception as e:
        logger.warning("execute_order: %s", e)
        return

#🔒PRIVATE
async def get_account_balance():
    """return account balance."""
    balance = "🏦 Balance\n"
    try:
        if exchange_type == 'dex':
            balance += await dex.get_account_balance()
        else:
            raw_balance = cex.fetch_free_balance()
            filtered_balance = {k: v for k, v in
                                raw_balance.items()
                                if v is not None and v>0}
            balance += "".join(f"{iterator}: {value} \n" for
                                iterator, value in
                                filtered_balance.items())
            if not balance:
                balance += "No Balance"
        return balance
    except Exception as e:
        logger.warning("get_account_balance: %s", e)

async def get_base_trading_symbol_balance():
    """return main instrument balance."""
    try:
        if exchange_type == 'dex':
            return await dex.get_basecoin_balance()
        cex_base_trading_symbol ='USDT'
        return cex.fetchBalance()[f'{cex_base_trading_symbol}']['free']
    except Exception as e:
        logger.warning("get_base_trading_symbol_balance: %s", e)
        await notify_error("Check  balance")

async def get_account_position():
    """return account position."""
    try:
        position = "📊 Position\n"
        if exchange_type == 'dex':
            open_positions = await dex.get_account_position()
        else:
            open_positions = cex.fetch_positions()
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


#🦾BOT ACTIONS
async def post_init():
    """TBD"""
    logger.info("Bot is online %s", __version__)
    await notify(f"Bot is online {__version__}")

async def help_command():
    helpcommand = """
    🏦<code>/bal</code>
    📦<code>buy btc/usdt sl=1000 tp=20 q=1%</code>
        <code>buy cake</code>
    🔀 <code>/trading</code>"""
    if settings.discord_webhook_id:
        helpcommand= helpcommand.replace("<code>", "`")
        helpcommand= helpcommand.replace("</code>", "`")
    bot_menu_help = f"{__version__}\n{helpcommand}"
    return f"{bot_menu_help}"

async def account_balance_command():
    """TBD"""
    logger.info("account_bal_command")
    return await get_account_balance()

async def account_position_command():
    """TBD"""
    return await get_account_position()

async def trading_switch_command():
    """TBD"""
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    return f"Trading is {bot_trading_switch}"

async def restart_command():
    """TBD"""
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

#🤖BOT
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
                await bot.start(
                                settings.bot_token
                                )
            elif settings.matrix_hostname:
                # MATRIX
                config = botlib.Config()
                config.emoji_verify = True
                config.ignore_unverified_devices = True
                config.store_path ='./config/matrix/'
                creds = botlib.Creds(
                            settings.matrix_hostname,
                            settings.matrix_user,
                            settings.matrix_pass
                            )
                bot = botlib.Bot(creds,config)
                @bot.listener.on_startup
                async def room_joined(room):
                    await post_init()
                @bot.listener.on_message_event
                async def on_matrix_message(room, message):
                    await parse_message(message.body)
                await bot.api.login()
                bot.api.async_client.callbacks = botlib.Callbacks(
                                                    bot.api.async_client, 
                                                    bot
                                                    )
                await bot.api.async_client.callbacks.setup_callbacks()
                for action in bot.listener._startup_registry:
                    for room_id in bot.api.async_client.rooms:
                        await action(room_id)
                await bot.api.async_client.sync_forever(timeout=3000, full_state=True)
            elif settings.telethon_api_id:
                # TELEGRAM
                bot = await TelegramClient(
                            None,
                            settings.telethon_api_id,
                            settings.telethon_api_hash
                            ).start(
                                bot_token=settings.bot_token
                                )
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


#⛓️API
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

#🙊TALKYTRADER
if __name__ == '__main__':
    """Launch Talky"""
    uvicorn.run(app, host=settings.host, port=settings.port)