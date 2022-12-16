##=============== VERSION =============
TTVersion="🪙TT 0.9.9"
##=============== import  =============
##log
import logging
import sys
import traceback

##env
import os
from os import getenv
from dotenv import load_dotenv
import json, requests

#telegram
import telegram
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

#notification
import apprise

#db
from tinydb import TinyDB, Query
import re

#CEX
import ccxt

#DEX
from web3 import Web3
#from web3.contract import Contract
from typing import List #Dict, List
import time

##=============== Logging  =============
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(msg=f"{TTVersion}")
logger.info(msg=f"python {sys.version}")
logger.info(msg=f"{ccxt.__version__}")
##=============== CONFIG ===============
dotenv_path = './config/.env'
db_path= './config/db.json'
#===================
db = TinyDB(db_path)
q = Query()
globalDB = db.table('global')
env = globalDB.all()[0]['env']
logger.info(msg=f"Environment is {env}")
telegramDB = db.table('telegram')
cexDB = db.table('cex')
dexDB = db.table('dex')
#===================
#global exchangeid
#global ex 
#global messaging
#global address
exchanges = {}
trading=True
testmode=False
#===================
commandlist= """
<code>/bal</code>
<code>/cex binance</code>
<code>/cex kraken</code>
<code>/cec binancecoinm</code>
<code>/dex pancake</code>
<code>/trading</code>
<code>/testmode</code>"""
menu=f'{TTVersion} \n {commandlist}\n'
#=============== functions ===============
def Convert(string):
    li = list(string.split(" "))
    return li

def LoadExchange(exchangeid, mode):
    global ex
    Ex_CEX=cexDB.search(q.name=={exchangeid})
    if Ex_CEX:
        if mode:
            newex=cexDB.search((q.name=={exchangeid})&(q.testmode=="True"))
        else:
            newex=cexDB.search((q.name=={exchangeid})&(q.testmode!="True"))
        if len(newex):
            exchange = getattr(ccxt, exchangeid)
            exchanges[exchangeid] = exchange()
            try:
                exchanges[exchangeid] = exchange({
                    'apiKey': newex[0]['api'],
                    'secret': newex[0]['secret']
                    })
                ex=exchanges[exchangeid]
                if testmode:
                    ex.set_sandbox_mode('enabled')
                else:
                    return ex
            except ccxt.NetworkError as e:
                logger.error(msg=f"network error {e}")
            except ccxt.ExchangeError as e:
                logger.error(msg=f"exchange error {e}")
            except Exception as e:
                logger.error(msg=f"{e}")
    else:
        ex=DEXLoadExchange(exchangeid, mode)

def DEXLoadExchange(exchangeid,mode):
    global ex
    global address
    global router
    global privatekey
    global tokenlist
    global abiurl
    global abiurltoken
    Ex_DEX=dexDB.search((q.name.matches(f'{exchangeid}',flags=re.IGNORECASE)))
    if Ex_DEX:
        if mode:
            newex=dexDB.search((q.name.matches(f'{exchangeid}',flags=re.IGNORECASE))&(q.testmode=="True"))
        else:
            newex=dexDB.search((q.name.matches(f'{exchangeid}',flags=re.IGNORECASE))&(q.testmode!="True"))
        if len(newex):
            try:
                name= newex[0]['name']
                address= newex[0]['address']
                privatekey= newex[0]['privatekey']
                networkprovider= newex[0]['networkprovider']
                router= newex[0]['router']
                testmode=newex[0]['testmode']
                tokenlist=newex[0]['tokenlist']
                abiurl=newex[0]['abiurl']
                abiurltoken=newex[0]['abiurltoken']
                ex = Web3(Web3.HTTPProvider(networkprovider))
                if ex.net.listening:
                    logger.info(msg=f"{ex.net.listening}")
                    return name
            except Exception as e:
                logger.error(msg=f"web3 error: {e}")
                return {e}

def DEXContractLookup(symbol):
    url = requests.get(tokenlist)
    text = url.text
    token_list = json.loads(text)['tokens']
    target_token = [token for token in token_list if token['symbol'].lower() == symbol.lower()]
    return target_token[0]['address'] if len(target_token)  >  0 else None

def DEXFetchAbi(address):
    url = abiurl
    params = {
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": abiurltoken }
    resp = requests.get(url, params=params).json()
    abi = resp["result"]
    logger.info(msg=f"{abi}")
    return abi

def DEXBuy(tokenAddress, amountToBuy):
    global address
    global ex
    global privatekey
    global abiurltoken
    web3=ex
    transactionRevertTime = 30
    gasAmount = 100
    gasPrice = 5
    logger.info(msg=f"{web3}")
    logger.info(msg=f"{tokenAddress}")
    logger.info(msg=f"{amountToBuy}")
    try:
        if(tokenAddress != None):
            tokenToBuy = web3.is_checksum_address(tokenAddress)
            spend = web3.is_checksum_address("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")# wbnb contract
            contract = web3.eth.contract(address=router, abi=DEXFetchAbi(router))
            logger.info(msg=f"{contract}")
            nonce = web3.eth.get_transaction_count(address)
           # start = time.time()
            DEXtxn = contract.functions.swapExactETHForTokens(0,[spend, tokenToBuy],address,(int(time.time()) + transactionRevertTime)
            ).buildTransaction({
                'from': address,# based Token(BNB)
                'value': web3.to_wei(float(amountToBuy), 'ether'),
                'gas': gasAmount,
                'gasPrice': web3.to_wei(gasPrice, 'gwei'),
                'nonce': nonce,})
            try:
                signed_txn = web3.eth.account.sign_transaction(DEXtxn, privatekey)
                tx_token = web3.eth.send_raw_transaction(
                    signed_txn.rawTransaction)  # BUY THE TK
            except Exception as e:
                logger.error(msg=f" {e}")
                return e
            txHash = str(web3.to_hex(tx_token))
        # TOKEN BOUGHT
            checkTransactionSuccessURL = "https://api.bscscan.com/api?module=transaction&action=gettxreceiptstatus&txhash=" + \
                txHash + "&apikey=" + abiurltoken
            checkTransactionRequest = requests.get(
                url=checkTransactionSuccessURL)
            txResult = checkTransactionRequest.json()['status']

            if(txResult == "1"):
                logger.info(msg=f"{txHash}")
                return txHash
            else:
                logger.error(msg=f"transaction failed")
    except Exception as e:
        logger.error(msg=f"Error: {e}")
        return e

##============= variables ================
if os.path.exists(db_path):
    logger.info(msg=f"Existing DB found")
    tg=telegramDB.search(q.platform==env)
    TG_TK = tg[0]['token']
    TG_CHANNEL_ID = tg[0]['channel']
    ex=cexDB.all()
    CEX_name = ex[0]['name']
    CEX_api = ex[0]['api']
    CEX_secret = ex[0]['secret']
    CEX_password = ex[0]['password']
    CEX_test_mode = ex[0]['testmode']
    CEX_ordertype = ex[0]['ordertype']
    CEX_defaulttype = ex[0]['defaultType']

else:
    logger.warning(msg=f"no DB, env file")
    if os.path.exists(dotenv_path):
        logger.info(msg=f"env file found")
        load_dotenv(dotenv_path)
    else:
        logger.error(msg=f"no config")
# ENV VAR (via file or docker)
    TG_TK = os.getenv("TG_TK")
    TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
    CEX_name = os.getenv("EX_NAME")
    CEX_api = os.getenv("EX_YOURAPIKEY")
    CEX_secret = os.getenv("EX_YOURSECRET")
    CEX_password = os.getenv("EX_YOURPASSWORD")
    CEX_ordertype = os.getenv("EX_ORDERTYPE")
    CEX_defaulttype = os.getenv("EX_DEFAULTTYPE")
    CEX_test_mode = os.getenv("EX_SANDBOXMODE")

##=========== DB SETUP =============
    extodb=cexDB.search(q.api==CEX_api)
    if len(extodb):
        logger.info(msg=f"EX exists")
    else:
        cexDB.insert({
        "name": CEX_name,
        "api": CEX_api,
        "secret": CEX_secret,
        "password": CEX_password,
        "testmode": CEX_test_mode,
        "ordertype": CEX_ordertype,
        "defaultType": CEX_defaulttype})
    tgtodb=telegramDB.search(q.token==TG_TK)
    if len(tgtodb):
        logger.info(msg=f"bot is setup")
    else:
        telegramDB.insert({
            "token": TG_TK,
            "channel": TG_CHANNEL_ID,
            "platform": "PRD"
            })
    if (TG_TK==""):
        logger.error(msg=f"no TG TK")
        sys.exit()
    elif (CEX_name==""):
        logger.error(msg=f"missing cex")
        sys.exit()
    elif (CEX_name==""):
        logger.error(msg=f"no sandbox")

##======== APPRISE Setup ===============
apobj = apprise.Apprise()
apobj.add('tgram://' + str(TG_TK) + "/" + str(TG_CHANNEL_ID))
##============ CEX Setup ===============
LoadExchange(CEX_name,CEX_test_mode)
##========== startup message ===========
async def post_init(application: Application):
    logger.info(msg=f"bot is online")
    await application.bot.send_message(TG_CHANNEL_ID, f"Bot is online\n {env} Sandbox:{testmode}\n {menu}", parse_mode=constants.ParseMode.HTML)
##=============== help  ================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg= f"{env} {ex} Sandbox:{testmode}\n {menu}"
    await send(update,msg)
##========== view balance  =============
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ex
    Ex_CEX=cexDB.search(q.name.matches(f'{ex}',flags=re.IGNORECASE))

    if (Ex_CEX):
        try:
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            trimmedbal=""
            for iterator in bal:
                trimmedbal += (f"{iterator} : {bal[iterator]} \n")
            if(trimmedbal==""):
                trimmedbal="No Balance"
            msg=f"🏦 Balance \n{trimmedbal}"
        except ccxt.NetworkError as e:
            logger.error(msg=f"{e}")
            msg=f"⚠️{e}"
        except ccxt.ExchangeError as e:
            logger.error(msg=f"{e}")
            msg=f"⚠️{e}"
        except Exception as e:
            logger.error(msg=f"CCXT error: {e}")
            msg=f"⚠️{e}"
    else:
        try:
            bal = ex.eth.get_balance(address)
            bal = ex.from_wei(bal,'ether')
            msg = f"🏦 Balance: {bal}"
        except Exception as e:
            logger.error(msg=f"{e}")
            msg=f"⚠️ {e}"
    await send(update,msg)

#===== order parsing and placing ======
async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msgtxt = update.effective_message.text
    msgtxt_upper =msgtxt.upper()
    filter_lst = ['BUY', 'SELL']
    msg=""
    if [ele for ele in filter_lst if(ele in msgtxt_upper)]:
        if (trading==False):
            message="TRADING DISABLED"
            await send(update,message)
        else:
            Ex_CEX=cexDB.search((q.name=={ex}))
            if (Ex_CEX):
                try:
                    order_m = Convert(msgtxt_upper)
                    m_dir= order_m[0]
                    m_symbol=order_m[1]
                    m_sl=order_m[2][3:7]
                    m_tp=order_m[3][3:7]
                    m_q=order_m[4][2:-1]
                    m_ordertype=CEX_ordertype
                    logger.info(msg=f"Processing: {m_symbol} {m_ordertype} {m_dir} {m_sl} {m_tp} {m_q}")
                    #% of bal
                    m_price = float(ex.fetchTicker(f'{m_symbol}').get('last'))
                    totalusdtbal = ex.fetchBalance()['USDT']['free']
                    amountpercent=((totalusdtbal)*(float(m_q)/100))/float(m_price)
                    res = ex.create_order(m_symbol, m_ordertype, m_dir, amountpercent)
                    orderid=res['id']
                    timestamp=res['datetime']
                    symbol=res['symbol']
                    side=res['side']
                    amount=res['amount']
                    price=res['price']
                    response=f"🟢 ORDER Processed: \n order id {orderid} @ {timestamp} \n  {side} {symbol} {amount} @ {price}"
                except ccxt.NetworkError as e:
                    logger.error(msg=f"Network error {e}")
                    response=f"⚠️ Network error {e}"
                except ccxt.ExchangeError as e:
                    logger.error(msg=f"Exchange error: {e}")
                    response=f"⚠️ Exchange error: {e}"
                except Exception as e:
                    logger.error(msg=f"CCXT error: {e}")
                    response=f"⚠️ CCXT error: {e}"
                ##await send(update,response)
            else:
                order_m = Convert(msgtxt_upper)
                m_dir= order_m[0]
                logger.info(msg=f"{order_m[1]}")
                m_symbol=DEXContractLookup(order_m[1])
                #m_q=order_m[2][2:-1]
                m_q=1
                logger.info(msg=f"{m_symbol}")
                res=DEXBuy(m_symbol,m_q)
                response=f"{res}"
        await send(update,response)

    else: error_handler()


##======== trading switch  =============
async def TradingSwitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trading
    if (trading==False):
        trading=True
    else:
        trading=False
    message=f"Trading is {trading}"
    await send(update,message)

##=========== CEX DEX switch ============
async def SwitchEx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_ex  = update.effective_message.text
    newexmsg = Convert(msg_ex)
    newex=newexmsg[1]
    extype=newexmsg[0]
    global ex
    global CEX_test_mode
    logger.info(msg=f"{newex}")
    if extype=="/cex":
        if testmode:
            newex=cexDB.search((q.name=={newex})&(q.testmode=="True"))
            logger.info(msg=f"{newex}")
        else:
            newex=cexDB.search((q.name=={newex})&(q.testmode!="True"))
            logger.info(msg=f"{newex}")
        if len(newex):
            logger.info(msg=f"CEX for {newex}")
            CEX_name = newex[0]['name']
            CEX_test_mode = newex[0]['testmode']
            res = LoadExchange(CEX_name,CEX_test_mode)
            response = f"CEX is {res} \n "
        else:
            response = 'CEX not setup'
    else:
        newex=dexDB.search((q.name=={newex})&(q.testmode!="True"))
        name= newex[0]['name']
        mode= newex[0]['testmode']
        res = DEXLoadExchange(name,mode)
        response = f"DEX is {name}"
    await send(update,response)

##========== Test mode switch ===========
async def TestModeSwitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global testmode
    if (testmode==False):
        testmode=True
    else:
        testmode=False
    message=f"Sandbox is {testmode}"
    await send(update,message)

##============ DB COMMAND ===============
async def dropDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"db table dropped")
    db.drop_tables()

async def showDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"display db")
    message=f" db extract: \n {db.all()}"
    await send(update,message)

##=========== notify command ============
async def notify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"apprise testing")
    try:
        msg="This is a apprise notification test"
        await notify(msg)
    except Exception as e:
        logger.error(msg=f"error: {e}")

#=========== sendmessage command ========
async def send (self, messaging):
    try:
        await self.effective_chat.send_message(f"{messaging}", parse_mode=constants.ParseMode.HTML)
    except telegram.error as e:
        logger.error(msg=f"telegram error: {e}")
    except Exception as e:
        logger.error(msg=f"error: {e}")
#=========== notification command ========
async def notify(messaging):
    try:
        apobj.notify(
            body=messaging
        )
    except Exception as e:
        logger.error(msg=f"apprise error: {e}")
#=========  bot error handling ========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e=f"⚠️ {tb_trim}"
    logger.error(msg=f"{e}")
    message=f"{e}"
    await send(update,message)
#================== BOT =================
def main():
    try:
        application = Application.builder().token(TG_TK).post_init(post_init).build()

#Menus
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), TradingSwitch))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), SwitchEx))
        application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
        application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))
        application.add_handler(MessageHandler(filters.Regex('/notify'), notify_command))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), TestModeSwitch))
        application.add_error_handler(error_handler)
        #Run the bot
        application.run_polling()
    except Exception as e:
        logger.fatal("Bot failed to start. Error: " + str(e))

if __name__ == '__main__':
    main()

