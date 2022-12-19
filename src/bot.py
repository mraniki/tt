##=============== VERSION =============
TTVersion="🪙TT Beta 1.00"
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
import tinydb
from tinydb import TinyDB, Query
import re

#CEX
import ccxt

#DEX
import web3 
from web3 import Web3
from web3.contract import Contract
from typing import List #Dict, List
import time

##=============== Logging  =============
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(msg=f"{TTVersion}")
logger.info(msg=f"python {sys.version}")
logger.info(msg=f"TinyDB {tinydb.__version__}")
logger.info(msg=f"TPB {telegram.__version__}")
logger.info(msg=f"CCXT {ccxt.__version__}")
logger.info(msg=f"Web3 {web3.__version__}")
logger.info(msg=f"apprise {apprise.__version__}")
##=============== CONFIG ===============
dotenv_path = './config/.env'
db_path= './config/db.json'
#===================
try:
    db = TinyDB(db_path)
    q = Query()
    globalDB = db.table('global')
    env = globalDB.all()[0]['env']
    logger.info(msg=f"Environment is {env}")
    telegramDB = db.table('telegram')
    cexDB = db.table('cex')
    dexDB = db.table('dex')
except Exception as e:
    logger.warning(msg=f"no db")
#===================
global ex
exchanges = {}
trading=True
testmode="False"
#===================
commandlist= """
<code>/bal</code>
<code>/cex binance</code> <code>buy btcusdt sl=1000 tp=20 q=5%</code>
<code>/cex kraken</code> <code>buy btcusdt sl=1000 tp=20 q=5%</code>
<code>/cex binancecoinm</code> <code>buy btcbusd sl=1000 tp=20 q=5%</code>
<code>/dex pancake</code> <code>buy btcb</code>
<code>/dex quickswap</code> <code>buy wbtc</code>
<code>/trading</code>
<code>/testmode</code>"""
menu=f'{TTVersion} \n {commandlist}\n'
#=============== Functions ===============
def Convert(string):
    li = list(string.split(" "))
    return li

def SearchCEX(string1,string2):
    if type(string1) is str:
        query1 = ((q.name==string1)&(q['testmode'] == string2))
        CEXSearch = cexDB.search(query1)
        logger.info(msg=f"CEXSearch: {CEXSearch}")
        logger.info(msg=f"len(str(CEXSearch)): {len(str(CEXSearch))}")
        if (len(str(CEXSearch))==1):
            return CEXSearch
    elif type(string1) is not str:
        try:
            query1 = ((q.name==string1.name.lower())&(q['testmode'] == string2))
            CEXSearch = cexDB.search(query1)
            if (len(str(CEXSearch))==1):
                return CEXSearch
            else:
                return
        except Exception as e:
            return
    else:
        return

def SearchDEX(string1,string2):
    try:
        query = ((q.name==string1)&(q['testmode'] == string2))
        DEXSearch = dexDB.search(query)
        logger.info(msg=f"DEXSearch: {DEXSearch}")
        if (len(str(DEXSearch))==1):
            return DEXSearch
        else:
            return 
    except Exception as e:
        return 
             
def SearchEx(string1,string2):
    logger.info(msg=f"string1: {string1}")
    logger.info(msg=f"string2: {string2}")
    CEXCheck=SearchCEX(string1,string2)
    logger.info(msg=f"CEXCheck: {CEXCheck}")
    DEXCheck=SearchDEX(string1,string2)
    logger.info(msg=f"DEXCheck: {DEXCheck}")
    if (CEXCheck!= None):
        if(len(str(CEXCheck))==1):
            return CEXCheck[0]['name']
    elif (len(str(DEXCheck))==1):
        return DEXCheck[0]['name']
    else:
        logger.error(msg=f"Error with DB search {string1} {string2}")
        return None

async def LoadExchange(exchangeid, mode):
    global ex
    global name
    global networkprovider
    global address
    global privatekey
    global tokenlist
    global router
    global abiurl
    global abiurltoken
    global basesymbol
    logger.info(msg=f"exchangeid: {exchangeid}")
    logger.info(msg=f"mode: {mode}")
    CEXCheck=SearchCEX(exchangeid,mode)
    logger.info(msg=f"CEXCheck: {CEXCheck}")
    DEXCheck=SearchDEX(exchangeid,mode)
    logger.info(msg=f"DEXCheck: {DEXCheck}")
    if (CEXCheck!= None):
        if (len(str(CEXCheck))==1):
            newex=CEXCheck
            exchange = getattr(ccxt, exchangeid)
            exchanges[exchangeid] = exchange()
            try:
                exchanges[exchangeid] = exchange({'apiKey': newex[0]['api'],'secret': newex[0]['secret']})
                ex=exchanges[exchangeid]
                if (mode==True):
                    ex.set_sandbox_mode('enabled')
                    markets=ex.loadMarkets() 
                    #ex.verbose = True
                    #logger.info(msg=f"markets: {markets}")
                    return ex
                else:
                    markets=ex.loadMarkets ()
                    #ex.verbose = True
                    #logger.info(msg=f"markets: {markets}")
                    #logger.info(msg=f"ex: {ex}")
                    #logger.info(msg=f"ex: {ex.id}")
                    return ex
            except Exception as e:
                await HandleExceptions(e)
    elif (len(str(DEXCheck))==1):
        newex= DEXCheck
        name= newex[0]['name']
        address= newex[0]['address']
        privatekey= newex[0]['privatekey']
        networkprovider= newex[0]['networkprovider']
        router= newex[0]['router']
        mode=newex[0]['testmode']
        tokenlist=newex[0]['tokenlist']
        abiurl=newex[0]['abiurl']
        abiurltoken=newex[0]['abiurltoken']
        basesymbol=newex[0]['basesymbol']
        ex = Web3(Web3.HTTPProvider(networkprovider))
        if ex.net.listening:
            logger.info(msg=f"Connected to Web3 {ex}")
            return name 
    else:
        return

async def DEXContractLookup(symbol):
    try:
        url = requests.get(tokenlist)
        text = url.text
        token_list = json.loads(text)['tokens']
        #logger.info(msg=f"{token_list}")
        target_token = [token for token in token_list if token['symbol'] == symbol]
        return target_token[0]['address'] if len(target_token)  >  0 else None
        logger.info(msg=f"{target_token[0]['address']}")
    except Exception as e:
        await HandleExceptions(e)

async def DEXFetchAbi(address):
    try:
        url = abiurl
        params = {
            "module": "contract",
            "action": "getabi",
            "address": address,
            "apikey": abiurltoken }
        resp = requests.get(url, params=params).json()
        abi = resp["result"]
        #logger.info(msg=f"{abi}")
        return abi
    except Exception as e:
        await HandleExceptions(e)

async def DEXBuy(tokenAddress, amountToBuy):
    web3=ex
    transactionRevertTime = 10000
    gasAmount = 100
    gasPrice = 5
    tokenToBuy = web3.to_checksum_address(tokenAddress)
    tokenToSell = basesymbol
    amountToBuy = amountToBuy
    txntime = (int(time.time()) + transactionRevertTime)
    try:
        if(tokenToBuy != None):
            tokenToSell=web3.to_checksum_address(await DEXContractLookup(tokenToSell))
            dexabi= await DEXFetchAbi(router)
            contract = web3.eth.contract(address=router, abi=dexabi)
            nonce = web3.eth.get_transaction_count(address)
            path=[tokenToSell, tokenToBuy]
        try:
            DEXtxn = contract.functions.swapExactETHForTokens(0,path,address,txntime).build_transaction({
            'from': address, # based Token
            'value': web3.to_wei(float(amountToBuy), 'ether'),
            'gas': gasAmount,
            'gasPrice': web3.to_wei(gasPrice, 'gwei'),
            'nonce': nonce})
            signed_txn = web3.eth.account.sign_transaction(DEXtxn, privatekey)
            tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction) # BUY THE TK
            txHash = str(web3.to_hex(tx_token)) # TOKEN BOUGHT
            checkTransactionSuccessURL = abiurl + "?module=transaction&action=gettxreceiptstatus&txhash=" + \
            txHash + "&apikey=" + abiurltoken
            checkTransactionRequest = requests.get(url=checkTransactionSuccessURL)
            txResult = checkTransactionRequest.json()['status']
            if(txResult == "1"):
                #logger.info(msg=f"{txHash}")
                return txHash
            else:
                message="Transaction Failed"
                return message
        except Exception as e:
            message="Transaction Failed"
            await HandleExceptions(e)
            return message
    except Exception as e:
        await HandleExceptions(e)
        message="Transaction Failed"
        return message

##============= variables ================
if os.path.exists(db_path):
    logger.info(msg=f"Existing DB found")
    tg=telegramDB.search(q.platform==env)
    TG_TK = tg[0]['token']
    TG_CHANNEL_ID = tg[0]['channel']
    cexdb=cexDB.all()
    dexdb=dexDB.all()
    CEX_name = cexdb[0]['name']
    CEX_api = cexdb[0]['api']
    CEX_secret = cexdb[0]['secret']
    #CEX_password = cexdb[0]['password']
    # CEX_test_mode = cexdb[0]['testmode']
    CEX_ordertype = cexdb[0]['ordertype']
    CEX_defaulttype = cexdb[0]['defaultType']
else:
    logger.warning(msg=f"no DB, env file")
    if os.path.exists(dotenv_path):
        logger.info(msg=f"env file found")
        load_dotenv(dotenv_path)
    else:
        logger.warning("no env file, trying the env variable")
        try:
             #ENV VAR (via file or docker)
            TG_TK = os.getenv("TG_TK")
            TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
            CEX_name = os.getenv("EX_NAME")
            CEX_api = os.getenv("EX_YOURAPIKEY")
            CEX_secret = os.getenv("EX_YOURSECRET")
            CEX_password = os.getenv("EX_YOURPASSWORD")
            CEX_ordertype = os.getenv("EX_ORDERTYPE")
            CEX_defaulttype = os.getenv("EX_DEFAULTTYPE")
            CEX_test_mode = os.getenv("EX_SANDBOXMODE")
        except Exception as e:
            logger.error("no env variables")

##=========== DB SETUP =============
    if len(cexDB.search(q.api==CEX_api)):
        logger.info(msg=f"EX exists in DB")
    else:
        cexDB.insert({
        "name": CEX_name,
        "api": CEX_api,
        "secret": CEX_secret,
        "password": CEX_password,
        "testmode": CEX_test_mode,
        "ordertype": CEX_ordertype,
        "defaultType": CEX_defaulttype})
    if len(telegramDB.search(q.token==TG_TK)):
        logger.info(msg=f"token is already setup")
    else:
        telegramDB.insert({"token": TG_TK,"channel": TG_CHANNEL_ID,"platform": "PRD"})
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
##=============== help  ================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg= f"Environment: {env}\nExchange: {SearchEx(ex,testmode)} Sandbox: {testmode}\n {menu}"
    await send(update,msg)
##========== startup message ===========
async def post_init(application: Application):
    global ex
    logger.info(msg=f"Setting up exchange {CEX_name}")
    ex=CEX_name
    await LoadExchange(ex,testmode)
    logger.info(msg=f"bot is online")
    await application.bot.send_message(TG_CHANNEL_ID, f"Bot is online\nEnvironment: {env}\nExchange: {SearchEx(ex,testmode)} Sandbox: {testmode}\n {menu}", parse_mode=constants.ParseMode.HTML)

##========== view balance  =============
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if not isinstance(ex,web3.main.Web3):
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            trimmedbal=""
            for iterator in bal:
                trimmedbal += (f"{iterator} : {bal[iterator]} \n")
            if(trimmedbal==""):
                trimmedbal="No Balance"
            msg=f"🏦 Balance \n{trimmedbal}"
        else:
            bal = ex.eth.get_balance(address)
            bal = ex.from_wei(bal,'ether')
            msg = f"🏦 Balance: {bal}"
        await send(update,msg)
    except Exception as e:
        await HandleExceptions(e)
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
            if not (isinstance(ex,web3.main.Web3)):
                order_m = Convert(msgtxt_upper)
                m_dir= order_m[0]
                m_symbol=order_m[1]
                m_sl=order_m[2][3:7]
                m_tp=order_m[3][3:7]
                m_q=order_m[4][2:-1]
                m_ordertype=CEX_ordertype
                logger.info(msg=f"Processing: {m_symbol} {m_ordertype} {m_dir} {m_sl} {m_tp} {m_q}")
                #Check Balance
                bal = ex.fetch_free_balance()
                bal = {k: v for k, v in bal.items() if v is not None and v>0}
                logger.info(msg=f"bal: {bal}")
                if (len(str(bal))):
                ######## % of bal
                    m_price = float(ex.fetchTicker(f'{m_symbol}').get('last'))
                    totalusdtbal = ex.fetchBalance()['USDT']['free']
                    amountpercent=((totalusdtbal)*(float(m_q)/100))/float(m_price)
                ######## ORDER 
                    res = ex.create_order(m_symbol, m_ordertype, m_dir, amountpercent)
                    orderid=res['id']
                    timestamp=res['datetime']
                    symbol=res['symbol']
                    side=res['side']
                    amount=res['amount']
                    price=res['price']
                    response=f"🟢 ORDER Processed: \n order id {orderid} @ {timestamp} \n  {side} {symbol} {amount} @ {price}"
                else: 
                    response=f"⚠️ not enough money"
            elif (isinstance(ex,web3.main.Web3)):
                order_m = Convert(msgtxt_upper)
                m_dir= order_m[0]
                m_symbol=await DEXContractLookup(order_m[1])
                m_q=1  #m_q=order_m[2][2:-1]
                res=await DEXBuy(m_symbol,m_q)
                response=f"{res}"   
            else:
                logger.warning(msg=f"error with exchange type {type(ex)}")
                response=f"⚠️ error with exchange setup"
            await send(update,response)

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
    logger.info(msg=f"current ex {ex}")
    msg_ex  = update.effective_message.text
    newexmsg = Convert(msg_ex)
    newex=newexmsg[1]
    typeex=newexmsg[0]
    if (typeex=="/cex"):
        SearchCEXResults= SearchCEX(newex,testmode)
        CEX_name = SearchCEXResults[0]['name']
        CEX_test_mode = testmode
        res = await LoadExchange(CEX_name,CEX_test_mode)
        response = f"CEX is {ex}"
    elif (typeex=="/dex"):
        SearchDEXResults= SearchDEX(newex,testmode)
        DEX_name= SearchDEXResults[0]['name']
        DEX_test_mode= testmode
        logger.info(msg=f"DEX_test_mode: {DEX_test_mode}")
        logger.info(msg=f"DEX_name: {DEX_name}")
        res = await LoadExchange(DEX_name,DEX_test_mode)
        logger.info(msg=f"res: {res}")
        response = f"DEX is {DEX_name}"
    else:  
        response = f"Error. Exchange is {ex}"
    await send(update,response)
    logger.info(msg=f"newex {ex}")
    logger.info(msg=f"type {type(ex)}")
    logger.info(msg=f"isinstance {isinstance(ex,web3.main.Web3)}")

##========== Test mode switch ===========
async def TestModeSwitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global testmode
    if (testmode=="False"):
        testmode="True"
    else:
        testmode="False"
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
#=========== sendmessage command =========
async def send (self, messaging):
    try:
        await self.effective_chat.send_message(f"{messaging}", parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await HandleExceptions(e)
#=========== notification command =========
async def notify(messaging):
    try:
        apobj.notify(body=messaging)
    except Exception as e: 
        logger.error(msg=f"error: {e}")
#=========  overall error handling ========
async def HandleExceptions(e) -> None:
    try:
        e==""
        logger.error(msg=f"{e}")
    except KeyError:
        logger.error(msg=f"DB content error {e}")
        e=f"DB content error  {e}"  
    except ccxt.base.errors:
        logger.error(msg=f"CCXT error {e}")
        e=f"CCXT error {e}"
    except ccxt.NetworkError:
        logger.error(msg=f"Network error {e}")
        e=f"Network error {e}"
    except ccxt.ExchangeError:
        logger.error(msg=f"Exchange error: {e}")
        e=f"Exchange error: {e}"
    except telegram.error:
        logger.error(msg=f"telegram error: {e}")
        e=f"telegram error: {e}"
    except Exception:
        logger.error(msg=f"error: {e}")
        e=f"{e}"
    message=f"⚠️ {e}"
    await notify(message)
#===========bot error handling ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e=f"{tb_trim}"
    message=f"⚠️ {e}"
    await send(update,message)
#================== BOT =================
def main():
    try:
#Starting Bot TPB
        application = Application.builder().token(TG_TK).post_init(post_init).build()

#TPBMenusHandlers
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), TradingSwitch))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), SwitchEx))
        application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
        application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), TestModeSwitch))
        application.add_error_handler(error_handler)
#Run the bot
        application.run_polling()
    except Exception as e:
        logger.fatal("Bot failed to start. Error: " + str(e))

if __name__ == '__main__':
    main()
