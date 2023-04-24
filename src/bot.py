##========== TalkyTrader 🪙🗿 ========

__version__ = "1.0.2"

##=============== import  =============

import logging, sys, json, requests, asyncio
from fastapi import FastAPI
import uvicorn

from config import settings

from findmyorder import findmyorder
import ccxt
from dxsp import DexSwap

#import telegram
from telegram.ext import Application, MessageHandler
#import telethon
from telethon import TelegramClient, events
#matrix
import simplematrixbotlib as botlib
#discord
import discord
#notification
import apprise
from apprise import NotifyFormat

#Utils
from ping3 import ping


#🧐LOGGING
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=settings.LOGLEVEL)
logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.getLogger('discord').setLevel(logging.WARNING)

#🔁UTILS

async def parse_message(self,msg):
    logger.debug(msg=f"self {self} msg {msg}")
    if self.effective_message.text: #tgram to be reviewed
        msg=self.effective_message.text
        logger.debug(msg=f"content {self['channel_post']['text']}")
    if not msg:
        return
    wordlist = msg.split(" ")
    wordlistsize = len(wordlist)
    logger.debug(msg=f"parse_message wordlist {wordlist} len {wordlistsize}")
    try:
        orderparsing = await order_parsing(msg)
        logger.debug(msg=f"orderparsing {orderparsing}")
    except:
        pass
    response = ""
    #🦾BOT FILTERS
    filters = {
        'ignore': ['⚠️', 'error', 'Environment:', 'Balance', 'Bot'],
        'order': ['BUY', 'SELL', 'buy', 'sell', 'Buy','Sell'],
        'help': ['/echo', '/help', '/start'],
        'balance': ['/bal'],
        'position': ['/pos','/position'],
        'quote': ['/q'],
        'trading': ['/trading'],
        'test_mode': ['/testmode'],
        'restart': ['/restart'],
    }
    try:
        for name, keywords in filters.items():
            if any(keyword in wordlist for keyword in keywords):
                if name == 'balance':
                    response = await account_balance_command()
                elif name == 'help':
                    response = await help_command()
                elif name == 'ignore':
                    return
                elif name == 'order':
                    if wordlistsize > 1:
                        order_check = await order_parsing(msg)
                        logger.info(msg=f"Order parsing: {order_check}")
                        direction = wordlist[0].upper()
                        stoploss = 100
                        takeprofit = 100
                        quantity = 10
                        if wordlistsize > 2:
                            stoploss = wordlist[2][3:]
                            takeprofit = wordlist[3][3:]
                            quantity = wordlist[4][2:-1]
                        symbol = wordlist[1]
                        order=[direction,symbol,stoploss,takeprofit,quantity]
                        logger.info(msg=f"Order identified: {order}")
                        res = await execute_order(order[0],order[1],order[2],order[3],order[4])
                        if res:
                            response = f"{res}"
                elif name == 'position':
                    response = await account_position_command()
                elif name == 'quote':
                    response = await quote_command(wordlist[1])
                elif name == 'restart':
                    response = await restart_command()
                elif name == 'trading':
                    response = await trading_switch_command()
                if response:
                    await notify(response)
    except Exception:
        logger.warning(msg="Parsing exception")

async def order_parsing(message_to_parse):
    logger.info(msg=f"order_parsing V2 with {message_to_parse}")
    try:
        fmo = findmyoder()
        return fmo.identify(message_to_parse)

    except Exception as e:
        logger.warning(msg=f"Order parsing error {e}")

async def verify_latency_ex():
    try:
        if ex_type == 'dex':
            return dex.latency
        else:
            round(ping("1.1.1.1", unit='ms'), 3)
    except Exception as e:
        logger.warning(msg=f"Latency error {e}")

#💬MESSAGING
async def notify(msg):
    if not msg:
        return
    apobj = apprise.Apprise()
    if (settings.DISCORD_WEBHOOK_ID):
        apobj.add(f'{bot_service}://{str(settings.DISCORD_WEBHOOK_ID)}/{str(settings.DISCORD_WEBHOOK_TOKEN)}')
    elif (settings.MATRIX_HOSTNAME):
        apobj.add(f"matrixs://{settings.MATRIX_USER}:{settings.MATRIX_PASS}@{settings.MATRIX_HOSTNAME[8:]}:443/{str(settings.BOT_CHANNEL_ID)}")
    else:
        apobj.add(f'tgram://{str(settings.BOT_TOKEN)}/{str(settings.BOT_CHANNEL_ID)}')
    try:
        await apobj.async_notify(body=msg, body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.warning(msg=f"{msg} not sent due to error: {e}")

#💱EXCHANGE
async def load_exchange():
    logger.info(msg="Setting up exchange")
    global ex_type
    global ex_name
    global ex_test_mode

    if (settings.CEX_API):
        defaultType =  settings.CEX_DEFAULTTYPE
        client = getattr(ccxt, settings.CEX_NAME)
        ex_test_mode = False
        try:
            if (defaultType!="SPOT"):
                cex = client({'apiKey': settings.CEX_API,'secret': settings.CEX_SECRET,'options': {'defaultType': settings.CEX_DEFAULTTYPE,    }, })
            else:
                cex = client({'apiKey': settings.CEX_API,'secret': settings.CEX_SECRET, })
            price_type = settings.CEX_ORDERTYPE
            if (settings.CEX_TESTMODE=='True'):
                logger.info(msg="sandbox setup")
                cex.set_sandbox_mode('enabled')
                ex_test_mode = True
                ex_name = settings.CEX_NAME
            markets = cex.load_markets()
            logger.debug(msg=f"CEX object created {cex}")
            ex_type = 'cex'
        except Exception as e:
            await handle_exception(e)

    elif (settings.DEX_CHAINID):
        chain_id = settings.DEX_CHAINID
        wallet_address = settings.DEX_WALLET_ADDRESS
        private_key = settings.DEX_PRIVATE_KEY
        block_explorer_api = settings.DEX_BLOCK_EXPLORER_API

        rpc = settings.DEX_RPC

        ex_name = settings.DEX_NAME
        ex_test_mode = settings.DEX_TESTMODE
        base_trading_symbol = settings.DEX_BASE_TRADING_SYMBOL
        protocol_type = settings.DEX_PROTOCOL
        router = settings.DEX_ROUTER
        amount_trading_option = settings.DEX_AMOUNT_TRADING_OPTION

        try:
            dex = DexSwap(chain_id=chain_id,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api)
            logger.debug(msg=f"DEX object created{dex}")
            ex_type = 'dex'
        except Exception as e:
            await handle_exception(e)
    else:
        logger.warning(msg="no CEX or DEX config found")
        return

#📦ORDER
async def execute_order(direction,symbol,stoploss,takeprofit,quantity):
    if bot_trading_switch == False:
        return
    try:
        response = f"⬇️ {symbol}" if (direction=="SELL") else f"⬆️ {symbol}"
        if ex_type == 'dex':
            order = execute_order.dex(direction=direction,symbol=symbol,stoploss=stoploss,takeprofit=takeprofit,quantity=quantity)
            order_confirmation+= order['confirmation']
        else:
            if (await get_account_balance()=="No Balance"): 
                await handle_exception("Check your Balance")
                return
            asset_out_quote = float(cex.fetchTicker(f'{symbol}').get('last'))
            totalusdtbal = await get_base_trading_symbol_balance() ##cex.fetchBalance()['USDT']['free']
            amountpercent = (totalusdtbal)*(float(quantity)/100) / asset_out_quote
            order = cex.create_order(symbol, price_type, direction, amountpercent)
            order_confirmation+= f"\n➕ Size: {order['amount']}\n⚫️ Entry: {order['price']}\nℹ️ {order['id']}\n🗓️ {order['datetime']}"
        return order_confirmation

    except Exception as e:
        await handle_exception(f"Exception with order processing {e}")
        return

async def get_quote(symbol):
    if ex_type == 'dex':
        asset_out_quote = await dex.get_quote(symbol)
        return f"🦄{asset_out_quote} USD\n🖊️{chainId}: {symbol}"
    else:
        asset_out_quote = cex.fetch_ticker(symbol.upper())['last']
        return f"🏛️ {price} USD"
        

#🔒PRIVATE
async def get_account_balance():
    balance =f"🏦 Balance\n"
    try:
        if ex_type == 'dex':
            balance += get_account_balance.dex()
        else:
            raw_balance = cex.fetch_free_balance()
            filtered_balance = {k: v for k, v in bal.items() if v is not None and v>0}
            balance += "".join(f"{iterator}: {value} \n" for iterator, value in filtered_balance.items())
            if not balance:
                balance += "No Balance"
        return balance
    except Exception:
        return

async def get_base_trading_symbol_balance():
    try:
        if ex_type == 'dex':
            return dex.get_basecoin_balance()
        else:
            return cex.fetchBalance()[f'{CEX_BASE_TRADING_SYMBOL}']['free']
    except Exception:
        await handle_exception("Check your balance")

async def get_account_position():
    try:
        position = f"📊 Position\n"
        if ex_type == 'dex':
            open_positions = await dex.get_account_position()
        else:
            open_positions = cex.fetch_positions()
            open_positions = [p for p in positions if p['type'] == 'open']
        logger.debug(msg=f"open_positions {open_positions}")
        position += open_positions
        return position
    except Exception:
        await handle_exception("Error when retrieving position")

async def get_account_margin():
    try:
        return
    except Exception as e:
        await handle_exception(e)
        return

#======= error handling
async def handle_exception(e) -> None:
    msg = ""
    logger.error(msg=f"error: {e}")
    message = f"⚠️ {msg} {e}"
    logger.error(msg = f"{message}")
    await notify(message)

#🦾BOT ACTIONS
async def post_init():
    startup_message=f"Bot is online {__version__}"
    logger.info(msg = f"{startup_message}")
    await notify(startup_message)

async def help_command():
    bot_ping = await verify_latency_ex()
    helpcommand = """
    🏦<code>/bal</code>
    📦<code>buy btc/usdt sl=1000 tp=20 q=1%</code>
        <code>buy cake</code>
    🦎 <code>/q BTCB</code>
           <code>/q WBTC</code>
           <code>/q btc/usdt</code>
    🔀 <code>/trading</code>"""
    if settings.DISCORD_WEBHOOK_ID:
        helpcommand= helpcommand.replace("<code>", "`")
        helpcommand= helpcommand.replace("</code>", "`")
    bot_menu_help = f"{__version__}\n{helpcommand}"
    return f"Environment: {defaultenv} Ping: {bot_ping}ms\nExchange: {ex_name} Sandbox: {ex_test_mode}\n{bot_menu_help}"

async def account_balance_command():
    return await get_account_balance()

async def account_position_command():
    return await get_account_position()

async def quote_command(symbol):
    return await get_quote(symbol)

async def trading_switch_command():
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    return f"Trading is {bot_trading_switch}"

async def restart_command():
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

#🤖BOT
async def bot():
    global bot
    try:
        await load_exchange()
        while True:
    #StartTheBot
            if settings.DISCORD_WEBHOOK_ID:
                intents = discord.Intents.default()
                intents.message_content = True
                bot = discord.Bot(intents=intents)
                @bot.event
                async def on_ready():
                    await post_init()
                @bot.event
                async def on_message(message: discord.Message):
                    await parse_message(message,message.content)
                await bot.start(settings.BOT_TOKEN)
            elif settings.MATRIX_HOSTNAME:
                config = botlib.Config()
                config.emoji_verify = True
                config.ignore_unverified_devices = True
                config.store_path ='./config/matrix/'
                creds = botlib.Creds(settings.MATRIX_HOSTNAME, settings.MATRIX_USER, settings.PASS)
                bot = botlib.Bot(creds,config)
                @bot.listener.on_startup
                async def room_joined(room):
                    await post_init()
                @bot.listener.on_message_event
                async def on_matrix_message(room, message):    
                    await parse_message(bot,message.body)
                await bot.api.login()
                bot.api.async_client.callbacks = botlib.Callbacks(bot.api.async_client, bot)
                await bot.api.async_client.callbacks.setup_callbacks()
                for action in bot.listener._startup_registry:
                    for room_id in bot.api.async_client.rooms:
                        await action(room_id)
                await bot.api.async_client.sync_forever(timeout=3000, full_state=True)
            elif settings.TELETHON_API_ID:
                bot = await TelegramClient(None, settings.TELETHON_API_ID, settings.TELETHON_API_HASH).start(bot_token=settings.BOT_TOKEN)
                await post_init()
                @bot.on(events.NewMessage())
                async def telethon(event):
                    await parse_message(bot,event.message.message)
                await bot.run_until_disconnected()
            elif settings.BOT_TOKEN:
                bot = Application.builder().token(settings.BOT_TOKEN).build()
                await post_init()
                bot.add_handler(MessageHandler(None, parse_message))
                async with bot:
                    await bot.initialize()
                    await bot.start()
                    await bot.updater.start_polling(drop_pending_updates=True)
            else:
                logger.error(msg="Check your messaging platform settings")
                await asyncio.sleep(10000)
                #sys.exit()
    except Exception as e:
        logger.error(msg=f"Bot not started: {str(e)}")

#⛓️API
app = FastAPI(title="TALKYTRADER",)

@app.on_event("startup")
def startup_event():
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(bot())
        logger.info(msg="Webserver started")
    except Exception as e:
        loop.stop()
        logger.error(msg=f"Bot start error: {str(e)}")

@app.on_event('shutdown')
async def shutdown_event():
    global uvicorn
    logger.info('Webserver shutting down...')
    uvicorn.keep_running = False

@app.get("/")
def root():
    return {f"Bot is online {__version__}"}

@app.get("/health")
def health_check():
    logger.info(msg="Healthcheck_Ping")
    return {f"Bot is online {__version__}"}

#🙊TALKYTRADER
if __name__ == '__main__':
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

