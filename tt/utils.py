__version__ = "3.0.21"

import asyncio
import importlib
import pkgutil
from apprise import Apprise, NotifyFormat
import time
import os
import sys
import socket

import ping3
import ccxt
from dxsp import DexSwap
from findmyorder import FindMyOrder
from iamlistening import Listener
from tt.config import settings, logger


async def listener():
    """Launch Listener"""

    bot_listener = Listener()
    task = asyncio.create_task(bot_listener.run_forever())

    while True:
        try:
            msg = await bot_listener.get_latest_message()
            if msg:
                await parse_message(msg)
        except Exception as error:
            print(error)
    await task


async def notify(msg):
    """💬 MESSAGING """
    if not msg:
        return
    apobj = Apprise()
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
                message = await get_quote(symbol)
            elif command == settings.bot_command_bal:
                await account_balance_command()
            elif command == settings.bot_command_pos:
                message = await account_position_command()
            elif command == settings.bot_command_restart:
                await restart_command()
            if message is not None:
                await notify(message)

        # Order found
        if settings.trading_enabled and await fmo.search(msg):
            # Order parsing 
            order = await fmo.get_order(msg)
            # Order execution
            order = await execute_order(order)
            if order:
                await notify(order)

    except Exception as e:
        logger.error(e)

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


def get_host_ip() -> str:
    """Returns host IP """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((settings.ping, 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        pass

def get_ping(host: str = settings.ping) -> float:
    """Returnsping """
    response_time = ping3.ping(host, unit='ms')
    print(response_time)
    time.sleep(1)
    return round(response_time, 3)




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
        if isinstance(exchange, DexSwap):
            open_positions = await exchange.get_account_position()
        else:
            open_positions = exchange.fetch_positions()
            open_positions = [p for p in open_positions if p['type'] == 'open']
        position = "📊 Position\n" + str(open_positions)
        position += str(await get_account_margin())
        return position
    except Exception as e:
        logger.warning("account_position: %s", e)


async def get_account_margin():
    try:
        return "\n🪙 margin\n" + (
            str(0)
            if isinstance(exchange, DexSwap)
            else str(
                await exchange.fetch_balance(
                    {
                        'type': 'margin',
                    }
                )
            )
        )
    except Exception as e:
        logger.warning("account_margin: %s", e)


# 🦾BOT ACTIONS
async def init_message():
    version = __version__
    # version = "2.2.2"
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


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self, package_name):
        logger.info("Loading plugin from package loaded:  %s", package)
        package = importlib.import_module(package_name)
        logger.info("Package loaded:  %s", package)
    
        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{plugin_name}")
    
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                        plugin_instance = obj()
                        self.plugins[plugin_name] = plugin_instance
                        logger.info("Plugin loaded:  %s", plugin_name)
    
            except Exception as e:
                logger.warning("error loading plugin:  %s", plugin_name)

    async def start_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]
            await plugin_instance.start()
        else:
            logger.warning("Plugin not found:  %s", plugin_name)

    async def start_all_plugins(self):
        for plugin_instance in self.plugins.values():
            await plugin_instance.start()


class BasePlugin:
    def start(self):
        pass

    def stop(self):
        pass

    async def listen(self):
        pass

    async def notify(self, message):
        pass
