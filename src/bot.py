"""
TalkyTrader 🪙🗿
"""
__version__ = "2.1.2"

import http
import os
import sys
import asyncio
import socket
import uvicorn
import ping3
from fastapi import FastAPI, Request

import ccxt
from dxsp import DexSwap
from findmyorder import FindMyOrder
from iamlistening import Listener

import apprise
from apprise import NotifyFormat

from .config import settings, logger


async def parse_message(msg):
    """main parser"""

    try:
        # Initialize FindMyOrder
        fmo = FindMyOrder()

        # Check ignore
        if msg.startswith(settings.bot_ignore):
            return
        # Check bot command
        if msg.startswith(settings.bot_prefix):
            message = None
            command = (msg.split(" ")[0])[1:]
            if command == settings.bot_command_help:
                message = f"{settings.bot_msg_help}\n{await init_message()}"
            elif command == settings.bot_command_trading:
                message = await trading_switch_command()
            elif command == settings.bot_command_quote:
                symbol = msg.split(" ")[1]
                await get_quote(symbol)
            elif command == settings.bot_command_bal:
                await account_balance_command()
            elif command == settings.bot_command_pos:
                await account_position_command()
            elif command == settings.bot_command_restart:
                await restart_command()
            if message is not None:
                await notify(message)

        # Order Process
        if settings.trading_enabled and await fmo.search(msg):
            # Order found
            order = await fmo.get_order(msg)
            order = await execute_order(order)
            if order:
                await notify(order)

    except Exception as e:
        logger.error(e)

async def notify(msg):
    """💬 MESSAGING """
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
    """Returns host IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((settings.ping, 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        pass

def get_ping(host: str = settings.ping) -> float:
    """Returns  ping """
    response_time = ping3.ping(host, unit='ms')
    return round(response_time, 3)


async def load_exchange():
    """load_exchange."""
    global exchange
    try:
        if settings.cex_name:
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
        elif settings.dex_chain_id:
            exchange = DexSwap()
        return exchange
    except Exception as e:
        logger.warning("exchange: %s", e)


async def execute_order(order_params):
    """Execute order."""

    action = order_params.get('action')
    instrument = order_params.get('instrument')
    quantity = order_params.get('quantity', settings.trading_risk_amount)

    try:
        if not action or not instrument:
            return

        if isinstance(exchange, DexSwap):
            trade = await exchange.execute_order(order_params)
            if not trade:
                return

            trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
            trade_confirmation += trade['confirmation']

        else:
            if await get_account_balance() == "No Balance":
                await notify("⚠️ Check Balance")
                return

            asset_out_quote = float(exchange.fetchTicker(f'{instrument}').get('last'))
            asset_out_balance = await get_trading_asset_balance()

            if not asset_out_balance:
                return

            transaction_amount = (asset_out_balance * (float(quantity) / 100) / asset_out_quote)

            trade = exchange.create_order(
                instrument,
                settings.cex_ordertype,
                action,
                transaction_amount
            )

            if not trade:
                return

            trade_confirmation = f"⬇️ {instrument}" if (action == "SELL") else f"⬆️ {instrument}\n"
            trade_confirmation += f"➕ Size: {round(trade['amount'], 4)}\n"
            trade_confirmation += f"⚫️ Entry: {round(trade['price'], 4)}\n"
            trade_confirmation += f"ℹ️ {trade['id']}\n"
            trade_confirmation += f"🗓️ {trade['datetime']}"

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


async def get_name():
    """Return exchange name"""
    try:
        return (
            await exchange.get_name()
            if isinstance(exchange, DexSwap)
            else exchange.id)
    except Exception as e:
        logger.warning("Failed to get exchange: %s", e)


async def get_account(exchange):
    """Return exchange account"""
    try:
        return (exchange.account
                if isinstance(exchange, DexSwap)
                else str(exchange.uid))
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
    """return main asset balance."""
    try:
        if isinstance(exchange, DexSwap):
            return await exchange.get_trading_asset_balance()
        else:
            return exchange.fetchBalance()[f"{settings.trading_asset}"]["free"]
    except Exception as e:
        await notify(f"⚠️ Check balance {settings.trading_asset}: {e}")


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
        exchange_name = await get_name()
        account_info = await get_account(exchange)
        start_up = f"🗿 {version}\n🕸️ {ip}\n🏓 {ping}\n💱 {exchange_name}\n🪪 {account_info}"
    except Exception:
        start_up = f"🗿 {version}\n"
    return start_up


async def post_init():
    # Notify bot startup
    await notify(await init_message())


async def account_balance_command():
    # Return account balance
    return await get_account_balance()


async def account_position_command():
    """Return account position"""
    return await get_account_position()


async def trading_switch_command():
    settings.trading_enabled = not settings.trading_enabled
    return f"Trading is {'enabled' if settings.trading_enabled else 'disabled'}."


async def restart_command():
    # Restart bot
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

# 🤖BOT


async def talky():
    """Launch Listener"""
    try:
        await load_exchange()
    except Exception as e:
        logger.error("exchange: %s", e)

    listener = Listener()
    task = asyncio.create_task(listener.run_forever())
    while True:
        try:
            msg = await listener.get_latest_message()
            if msg:
                await parse_message(msg)
        except Exception as error:
            print(error)
    await task

# ⛓️API
app = FastAPI(title="TALKYTRADER",)


@app.on_event("startup")
def startup_event():
    """fastapi startup"""
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(talky())
        logger.info("started")
    except Exception as e:
        loop.stop()
        logger.error("Bot KO: %s", e)


@app.on_event('shutdown')
async def shutdown_event():
    """fastapi shutdown"""
    global uvicorn
    logger.info("shutting down")
    uvicorn.keep_running = False


@app.get("/")
async def root():
    """fastapi root"""
    return await init_message()


@app.get("/health")
async def health_check():
    """fastapi health"""
    return await init_message()


@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request):
    payload = await request.body()
    if payload["key"] == settings.webhook_secret:
        await notify(payload)

# 🙊TALKYTRADER


if __name__ == '__main__':
    """Launch Talky"""
    uvicorn.run(app, host=settings.host, port=int(settings.port))
