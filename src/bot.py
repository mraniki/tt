##=============== VERSION =============
version="🪙TT Beta 1.3.3"
##=============== import  =============
##log
import logging
import sys
import traceback
from ping3 import ping, verbose_ping
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
from typing import List
import time
from datetime import datetime
from pycoingecko import CoinGeckoAPI
##=============== Logging  =============
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
##=============== CONFIG ===============
# dotenv_path = './config/.env'
load_dotenv() #.env
db_path= './config/db.json'
contingency_db_path= './config/sample_db.json'
#===================
global ex
exchanges = {}
trading=True
testmode="True"
headers = { "User-Agent": "Mozilla/5.0" }
cg = CoinGeckoAPI()
#===================
fullcommandlist= """
<code>/bal</code>
<code>/cex kraken</code> <code>buy btc/usdt sl=1000 tp=20 q=1%</code> <code>/p btc/usdt</code>
<code>/cex binance</code> <code>buy btcusdt sl=1000 tp=20 q=1%</code> <code>/p btcusdt</code>
<code>/dex pancake</code> <code>buy cake</code> <code>/p BTCB</code>
<code>/trading</code>
<code>/testmode</code>"""
menuhelp=f"{version} \n {fullcommandlist}"
#========== Common Functions =============
def LibCheck():
    logger.info(msg=f"{version}")
    logger.info(msg=f"Python {sys.version}")
    logger.info(msg=f"TinyDB {tinydb.__version__}")
    logger.info(msg=f"TPB {telegram.__version__}")
    logger.info(msg=f"CCXT {ccxt.__version__}")
    logger.info(msg=f"Web3 {web3.__version__}")
    logger.info(msg=f"apprise {apprise.__version__}")
    return
##===========DB Functions
def DBCommand_Add_TG(s1,s2,s3):
    if len(telegramDB.search(q.token==s1)):
        logger.info(msg=f"token is already setup")
    else:
        telegramDB.insert({"token": s1,"channel": s2,"platform": s3})
def DBCommand_Add_CEX(s1,s2,s3,s4,s5,s6,s7):
    if len(cexDB.search(q.api==s2)):
        logger.info(msg=f"EX exists in DB")
    else:
        cexDB.insert({
        "name": s1,
        "api": s2,
        "secret": s3,
        "password": s4,
        "testmode": s5,
        "ordertype": s6,
        "defaultType": s7})
def DBCommand_Add_DEX(s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11):
    if len(dexDB.search(q.name==s1)):
        logger.info(msg=f"EX exists in DB")
    else:
        dexDB.insert({
            "name": s1,
            "walletaddress": s2,
            "privatekey": s3,
            "version": s4,
            "networkprovider": s5,
            "router": s6,
            "testmode": s7,
            "tokenlist":s8,
            "abiurl":s9,
            "abiurltoken":s10,
            "basesymbol":s11})
async def dropDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"db dropped")
    db.drop_tables()
async def showDB_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"display db")
    message=f" db extract: \n {db.all()}"
    await send(update,message)

#=========Exchange Functions
async def SearchCEX(s1,s2):
    if type(s1) is str:
        query1 = ((q.name==s1)&(q['testmode'] == s2))
        CEXSearch = cexDB.search(query1)
        if (len(str(CEXSearch))>=1):
            return CEXSearch
    elif type(string1) is not str:
        try:
            query1 = ((q.name==s1.name.lower())&(q['testmode'] == s2))
            CEXSearch = cexDB.search(query1)
            if (len(str(CEXSearch))==1):
                return CEXSearch
            else:
                return
        except Exception as e:
            await HandleExceptions(e)
            return
    else:
        return

async def SearchDEX(s1,s2):
    try:
        query = ((q.name==s1)&(q['testmode'] == s2))
        DEXSearch = dexDB.search(query)
        if (len(str(DEXSearch))>=1):
         logger.info(msg=f"{DEXSearch}")
         return DEXSearch
        else:
         return
    except Exception as e:
        await HandleExceptions(e)
        return

async def SearchEx(s1,s2):
    try:
      if (isinstance(s1,str)):
        CEXCheck= await SearchCEX(s1,s2)
        DEXCheck= await SearchDEX(s1,s2)
        if (CEXCheck!= None):
            if(len(str(CEXCheck))>=1):
                return CEXCheck[0]['name']
        elif (len(str(DEXCheck))>=1):
            return DEXCheck[0]['name']
      elif not (isinstance(s1,web3.main.Web3)):
        CEXCheck=await SearchCEX(s1.id,s2)
        return CEXCheck[0]['name']
      elif (isinstance(s1,web3.main.Web3)):
        DEXCheck=await SearchDEX(s1,s2)
        return name
      else:
        return
    except Exception as e:
        await HandleExceptions(e)
        return

async def LoadExchange(exchangeid, mode):
    global ex
    global name
    global networkprovider
    global version
    global walletaddress
    global privatekey
    global tokenlist
    global router
    global abiurl
    global abiurltoken
    global basesymbol
    global gasPrice
    global m_ordertype
    global gasLimit
    global router_instance
    global router_instanceabi
    global platform
    global chainId
    if (failsafe):
        ex = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        return
    logger.info(msg=f"Setting up {exchangeid}")
    CEXCheck= await SearchCEX(exchangeid,mode)
    DEXCheck= await SearchDEX(exchangeid,mode)
    if (CEXCheck):
        newex=CEXCheck
        exchange = getattr(ccxt, exchangeid)
        exchanges[exchangeid] = exchange()
        try:
            exchanges[exchangeid] = exchange({'apiKey': newex[0]['api'],'secret': newex[0]['secret']})
            m_ordertype=newex[0]['ordertype']
            ex=exchanges[exchangeid]
            # tickers = ex.fetch_tickers()
            # for symbol, ticker in tickers.items():
            #     print(
            #         symbol,
            #         ticker['datetime'],
            #         'high: ' + str(ticker['high']),
            #         'low: ' + str(ticker['low']),
            #         'bid: ' + str(ticker['bid']),
            #         'ask: ' + str(ticker['ask']),
            #         'volume: ' + str(ticker['quoteVolume'] or ticker['baseVolume'])
            #     )
            name=ex
            if (mode=="True"):
                ex.set_sandbox_mode('enabled')
                markets=ex.loadMarkets()
                logger.info(msg=f"ex: {ex}")
                #ex.verbose = True
                #logger.info(msg=f"markets: {markets}")
                return ex
            else:
                markets=ex.loadMarkets ()
                logger.info(msg=f"ex: {ex}")
                return ex

        except Exception as e:
            await HandleExceptions(e)
    elif (DEXCheck):
        newex= DEXCheck
        name= newex[0]['name']
        walletaddress= newex[0]['walletaddress']
        privatekey= newex[0]['privatekey']
        version= newex[0]['version']
        networkprovider= newex[0]['networkprovider']
        router= newex[0]['router']
        mode=newex[0]['testmode']
        tokenlist=newex[0]['tokenlist']
        abiurl=newex[0]['abiurl']
        abiurltoken=newex[0]['abiurltoken']
        basesymbol=newex[0]['basesymbol']
        gasLimit=newex[0]['gasLimit']
        gasPrice=newex[0]['gasPrice']
        platform=newex[0]['platform']
        chainId=newex[0]['platform']
        ex = Web3(Web3.HTTPProvider('https://'+networkprovider))
        #ex = Web3(Web3.HTTPProvider(networkprovider))
        router_instanceabi= await DEXFetchAbi(router) #Router ABI
        router_instance = ex.eth.contract(address=router, abi=router_instanceabi) #ContractLiquidityRouter
        if ex.net.listening:
            logger.info(msg=f"Connected to {ex}")
            return name
        else:
            raise ConnectionError(f'Could not connect to {router}')
    else:
        return


async def DEXContractLookup(symb):
    try:
        url = requests.get(tokenlist)
        text = url.text
        token_list = json.loads(text)['tokens']
        symb=symb.upper()
        try:
            symbolcontract = [token for token in token_list if token['symbol'] == symb]
            logger.info(msg=f"symbolcontract {symbolcontract}")
            if len(symbolcontract) > 0:
                #logger.info(msg=f"symbolcontract {symbolcontract[0]['address']}")
                return symbolcontract[0]['address']
            else:
                msg=f"{symb} does not exist in {tokenlist}"
                await HandleExceptions(msg)
                return
        except Exception as e:
            await HandleExceptions(e)
            return
    except Exception as e:
        await HandleExceptions(e)
        return

async def DEXFetchAbi(addr):
    try:
        url = abiurl
        params = {
            "module": "contract",
            "action": "getabi",
            "address": addr,
            "apikey": abiurltoken }
        resp = requests.get(url, params=params, headers=headers).json()
        abi = resp["result"]
        #logger.info(msg=f"{abi}")
        if(abi!=""):
            return abi
        else:
            return None
    except Exception as e:
        await HandleExceptions(e)

#ORDER PARSER
def Convert(s):
    li = s.split(" ")
    try:
        m_dir= li[0]
    except (IndexError, TypeError):
        logger.error(msg=f"{s} no direction")
        return
    try:
        m_symbol=li[1]
    except (IndexError, TypeError):
        logger.error(msg=f"{s} no symbol")
        return
    try:
        m_sl=li[2][3:7]
    except (IndexError, TypeError):
        logger.warning(msg=f"{s} no sl")
        m_sl=0
    try:
        m_tp=li[3][3:7]
    except (IndexError, TypeError):
        logger.warning(msg=f"{s} no tp")
        m_tp=0
    try:
        m_q=li[4][2:-1]
    except (IndexError, TypeError):
        logger.warning(msg=f"{s} no size default to 10 %")
        m_q=10
    order=[m_dir,m_symbol,m_sl,m_tp,m_q]
    logger.info(msg=f"order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
    return order

#========== Order function
async def SendOrder(s1,s2,s3,s4,s5):
    try:
      if not isinstance(ex,web3.main.Web3):
        logger.info(msg=f"order: {s1} {s2} {s3} {s4} {s5}")
        response = await SendOrder_CEX(s1,s2,s3,s4,s5)
      elif (isinstance(ex,web3.main.Web3)):
        response = await SendOrder_DEX(s1,s2,s3,s4,s5)
      return response
    except Exception as e:
      await HandleExceptions(e)
      return

async def SendOrder_CEX(s1,s2,s3,s4,s5):
    try:
        bal = ex.fetch_free_balance()
        bal = {k: v for k, v in bal.items() if v is not None and v>0}
        if (len(str(bal))):
            ######## % of bal
            m_price = float(ex.fetchTicker(f'{s2}').get('last'))
            totalusdtbal = ex.fetchBalance()['USDT']['free']
            amountpercent=((totalusdtbal)*(float(s5)/100))/float(m_price)
            try:
                res = ex.create_order(s2, m_ordertype, s1, amountpercent)
                orderid=res['id']
                timestamp=res['datetime']
                symbol=res['symbol']
                side=res['side']
                amount=res['amount']
                price=res['price']
                if (s1=="SELL"):
                    response = f"⬇️ {symbol}"
                else:
                    response = f"⬆️ {symbol}"
                # tokeninfo = cg.search(query = symbol)
                # logger.info(msg=f"tokeninfo {tokeninfo}")
                response+= f"\n➕ Size: {amount}\n⚫️ Entry: {price}\nℹ️ {orderid}\n🗓️ {timestamp}"
                return response
            except Exception as e:
                await HandleExceptions(e)
                return
    except Exception as e:
        await HandleExceptions(e)
        return

async def DEX_GasControl():
    CurrentGasPrice=int(ex.to_wei(ex.eth.gas_price,'wei'))
    logger.info(msg=f"CurrentGasPrice {CurrentGasPrice}")
    MyGasPrice=int(ex.to_wei(gasPrice,'gwei'))
    logger.info(msg=f"MyGasPrice {MyGasPrice}")
    if (CurrentGasPrice>=MyGasPrice):
        logger.warning(msg=f"{CurrentGasPrice} {MyGasPrice} ")
    else:
        logger.info(msg=f"gas setup{MyGasPrice} aligned with current gas price {CurrentGasPrice}")
    # checkgasLimitURL = abiurl + "?module=stats&action=dailyavggaslimit&startdate=2022-01-09&enddate=2022-01-09&sort=asc&apikey=" + abiurltoken
    # checkgasLimitRequest = requests.get(url=checkgasLimitURL,headers=headers)
    # gasLimitresults = checkgasLimitRequest.json()['result']['gasLimit']
    # logger.info(msg=f"gasLimitresults {gasLimitresults}")
    # if (gasLimit<=gasLimitresults):
    #     logger.warning(msg=f"gaslimit warning: {gasLimit} {gasLimitresults}")

async def DEX_Sign_TX(contract_tx):
    tx_fields = {
        'from': walletaddress,
        'gas': int(gasLimit),
        'gasPrice': ex.to_wei(gasPrice,'gwei'),
        'nonce': ex.eth.get_transaction_count(walletaddress),
    }
    tx = contract_tx.build_transaction(tx_fields)
    signed = ex.eth.account.sign_transaction(tx, privatekey)
    raw_tx = signed.rawTransaction
    return ex.eth.send_raw_transaction(raw_tx)

async def TokenPrice(s1):
    try:
        coininfo=cg.search(query=s1) 
        for i in coininfo['coins']:
            tokeninfo=i['symbol']
            if (tokeninfo==s1):
                logger.info(msg=f"{i['api_symbol']}")
                coininfo=cg.get_coin_by_id(id=i['api_symbol'])
                coinplatfrom=coininfo['asset_platform_id']
                logger.info(msg=f"coinplatfrom {coinplatfrom}")
                coinprice=coininfo['market_data']['current_price']['usd']
                logger.info(msg=f"coinprice {coinprice}")
                coinsymbol=coininfo['symbol']
                response = f'{coinsymbol} {coinprice} USD on {coinplatfrom}'
                logger.info(msg=f"{response}")
                return coinprice
    except Exception:
        return

async def SendOrder_DEX(s1,s2,s3,s4,s5):
    try:
        if (s1=="BUY"):
            tokenA=basesymbol
            tokenB=s2
        else:
            tokenA=s2
            tokenB=basesymbol
        tokenToSell=ex.to_checksum_address(await DEXContractLookup(tokenA))
        AbiTokenA= await DEXFetchAbi(tokenToSell) #tokenToSell ABI
        contractTokenA = ex.eth.contract(address=tokenToSell, abi=AbiTokenA) 
        approvalcheck = contractTokenA.functions.allowance(walletaddress, router).call()
        if (approvalcheck==0):
            maxamount = (ex.to_wei(2**64-1,'ether'))
            approval_TX = contractTokenA.functions.approve(router, maxamount)
            ApprovaltxHash = await DEX_Sign_TX(approval_TX)
            logger.info(msg=f"Approval {str(ex.to_hex(ApprovaltxHash))}")
            time.sleep(10) #wait approval
        tokenToBuy= ex.to_checksum_address(await DEXContractLookup(tokenB))
        OrderPath=[tokenToSell, tokenToBuy]
        tokeninfobal=contractTokenA.functions.balanceOf(walletaddress).call()
        tokeninfobaldecimal=contractTokenA.functions.decimals().call()
        if (s1=="SELL"):
            amountTosell = (tokeninfobal)/(10 ** tokeninfobaldecimal) #SELL all token in case of sell order
            response = f"⬇️ {s2}"
            coinprice= await TokenPrice(tokenA)
        else:
            amountTosell = ((tokeninfobal)/(10 ** tokeninfobaldecimal))*(float(s5)/100) #buy %p ercentage  
            response = f"⬆️ {s2}"
            coinprice= await TokenPrice(tokenB)
        logger.info(msg=f"coinprice {coinprice}")
        i_OrderAmount=(ex.to_wei(amountTosell,'ether'))
        OrderAmount = i_OrderAmount
        OptimalOrderAmount  = router_instance.functions.getAmountsOut(OrderAmount, OrderPath).call()
        MinimumAmount = int(OptimalOrderAmount[1] *0.98)# max 2% slippage
        logger.info(msg=f"Min received {ex.from_wei(MinimumAmount, 'ether')}")
        txntime = (int(time.time()) + 1000000)
        if (version=="v2"):
            {
            swap_TX = router_instance.functions.swapExactTokensForTokens(OrderAmount,MinimumAmount,OrderPath,walletaddress,txntime)
            tx_token = await DEX_Sign_TX(swap_TX)
            }
        elif (version =="v3"):
            {
                params = {
                'tokenIn': tokenToBuy,
                'tokenOut': tokenToSell,
                'fee': 3000,
                'recipient': walletaddress,
                'deadline': int((datetime.now() + timedelta(seconds=20)).timestamp()),
                'amountIn': ex.from_wei(MinimumAmount, 'ether'),
                'amountOutMinimum': 0,
                'sqrtPriceLimitX96': 0,
                }

                tx_params = {'value': ex.to_wei(0.000001, 'ether'),}

                swap_TX=router_instance.functions.exactInputSingle(params).buildTransaction(tx_params)
                tx = contract_tx.build_transaction(tx_fields)
                signed = ex.eth.account.sign_transaction(tx, privatekey)
                raw_tx = signed.rawTransaction
                return ex.eth.send_raw_transaction(raw_tx)
            }

        txHash = str(ex.to_hex(tx_token))
        logger.info(msg=f"{txHash}")
        checkTransactionSuccessURL = abiurl + "?module=transaction&action=gettxreceiptstatus&txhash=" + txHash + "&apikey=" + abiurltoken
        checkTransactionRequest = requests.get(url=checkTransactionSuccessURL,headers=headers)
        txResult = checkTransactionRequest.json()['status']
        await DEX_GasControl()
        txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
        tokenprice=coinprice
        gasUsed=txHashDetail['gasUsed']
        txtimestamp=datetime.now()
        if(txResult == "1"):
            response+= f"\n➕ Size: {round(ex.from_wei(MinimumAmount, 'ether'),5)}\n⚫️ Entry: {tokenprice}USD \nℹ️ {txHash}\n⛽️ {gasUsed}\n🗓️ {txtimestamp}"
            logger.info(msg=f"{response}")
            #logger.info(msg=f"{txHashDetail}")
            return response     
    except Exception as e:
        await HandleExceptions(e)
        return

async def TokenInfo(token):
    global tokenprice
    global tokeninfo
    #asset_platforms = cg.get_asset_platforms()
    #logger.info(msg=f"cg.get_asset_platforms {asset_platforms}")
    try:
        coininfo=cg.get_coin_by_id(id=token) 
        coinplatfrom=coininfo['asset_platform_id']
        coindescription=coininfo['description']['en']
        coinprice=coininfo['market_data']['current_price']['usd']
        coinsymbol=coininfo['symbol']
        coinlink='https://www.coingecko.com/en/coins/'+coininfo['symbol']
        response = f'{coinsymbol} {coinprice} USD \n{coindescription}\n{coinlink}'
        logger.info(msg=f"{response}")   
        return response
    except Exception:
        return
       
async def token_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tginput  = update.effective_message.text
    input = tginput.split(" ")
    symbol=input[1].upper()
    try:
        coininfo=cg.search(query=symbol) 
        #logger.info(msg=f"coininfo {coininfo}")
        for i in coininfo['coins']:
            tokeninfo=i['symbol']
            if (tokeninfo==symbol):
                logger.info(msg=f"Pass")
                logger.info(msg=f"{i['api_symbol']}")
                coininfo=cg.get_coin_by_id(id=i['api_symbol'])
                coinplatfrom=coininfo['asset_platform_id']
                logger.info(msg=f"coinplatfrom {coinplatfrom}")
                coinprice=coininfo['market_data']['current_price']['usd']
                logger.info(msg=f"coinprice {coinprice}")
                coinsymbol=coininfo['symbol']
                response = f'{coinsymbol} {coinprice} USD on {coinplatfrom}'
                logger.info(msg=f"{response}")
    except Exception as e:
        return

async def EX_Ping():
    if not isinstance(ex,web3.main.Web3):
        symbol = 'BTC/USDT'
        results = []
        num_iterations = 5
        for i in range(0, num_iterations):
            started = ex.milliseconds()
            orderbook = ex.fetch_order_book(symbol)
            ended = ex.milliseconds()
            elapsed = ended - started
            logger.info(msg=f"elapsed {elapsed}")
            results.append(elapsed)
        rtt = int(sum(results) / len(results))
        response = rtt
    elif (isinstance(ex,web3.main.Web3)):
        logger.info(msg=f"networkprovider {networkprovider}")
        response = round(ping(networkprovider, unit='ms'),3)
    return response
    
#=========== Send function
async def send (self, messaging):
    try:
        await self.effective_chat.send_message(f"{messaging}", parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await HandleExceptions(e)
#========== notification function
async def notify(messaging):
    try:
        apobj.notify(body=messaging)
    except Exception as e:
        logger.error(msg=f"error: {e}")
#======= error handling
async def HandleExceptions(e) -> None:
    try:
        e==""
        logger.error(msg=f"{e}")
    except KeyError:
        logger.error(msg=f"DB content error {e}")
        e=f"DB content error {e}"
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
##======== END OF FUNCTIONS ============

##============TG COMMAND================
##====view help =======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r_ping = await EX_Ping()
    msg= f"Environment: {env} Ping: {r_ping}ms\nExchange: {await SearchEx(ex,testmode)} Sandbox: {testmode}\n{menuhelp}"
    await send(update,msg)
##====restart =======
# async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     os.execv(__file__, sys.argv)
#     #os.execv(sys.executable, ['python'] + [sys.argv[0]])
#     #os.execv(sys.executable, ['python'] + os.path.abspath(sys.argv[0]))
##====view balance=====
async def bal_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg=f"🏦 Balance"
    try:
        if not isinstance(ex,web3.main.Web3):
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            sbal=""
            for iterator in bal:
                sbal += (f"{iterator}: {bal[iterator]} \n")
            if(sbal==""):
                sbal="No Balance"
            msg+=f"\n{sbal}"
        else:
            bal = ex.eth.get_balance(walletaddress)
            bal = round(ex.from_wei(bal,'ether'),5)
            msg += f"\n{bal}"
        await send(update,msg)
    except Exception as e:
        await HandleExceptions(e)

#===order parsing  ======
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
            order_m = Convert(msgtxt_upper)
            m_dir= order_m[0]
            m_symbol=order_m[1]
            m_sl=order_m[2]
            m_tp=order_m[3]
            m_q=order_m[4]
            logger.info(msg=f"Processing order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
            try:
                res=await SendOrder(m_dir,m_symbol,m_sl,m_tp,m_q)
                if (res!= None):
                    response=f"{res}"
                    await send(update,response)
            except Exception as e:
                await HandleExceptions(e)
                return
##======TG COMMAND view price ===========
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tginput  = update.effective_message.text
    input = tginput.split(" ")
    symbol=input[1]
    try:
        if not (isinstance(ex,web3.main.Web3)):
            price= ex.fetch_ticker(symbol.upper())['last']
            response=f"₿ {symbol} @ {price}"
        elif (isinstance(ex,web3.main.Web3)):
            if(await DEXContractLookup(symbol) != None):
                TokenToPrice = ex.to_checksum_address(await DEXContractLookup(symbol))
                logger.info(msg=f"token {TokenToPrice}")
                tokenToSell='USDT'
                basesymbol=ex.to_checksum_address(await DEXContractLookup(tokenToSell))
                qty=1
                if(TokenToPrice != None):
                    tokeninfo=cg.get_coin_info_from_contract_address_by_id(id=platform,contract_address=TokenToPrice)
                    tokenprice=tokeninfo['market_data']['current_price']['usd']
                    price = router_instance.functions.getAmountsOut(1, [TokenToPrice,basesymbol]).call()[1]
                    logger.info(msg=f"price {price}")
                    response=f"₿ {TokenToPrice}\n{symbol} @ {(price)} or {tokenprice}"
                    await DEX_TokenInfo(symbol)
                    await send(update,response)
    except Exception as e:
        await HandleExceptions(e)
        return
##======TG COMMAND coin info  ===========
async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tginput  = update.effective_message.text
    input = tginput.split(" ")
    symbol=input[1]
    try:
        response=await TokenInfo(symbol)
        await send(update,response)
    except Exception as e:
        await HandleExceptions(e)
        return
##====TG COMMAND Trading switch  ========
async def TradingSwitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trading
    if (trading==False):
        trading=True
    else:
        trading=False
    message=f"Trading is {trading}"
    await send(update,message)
##====TG COMMAND CEX DEX switch =========
async def SwitchEx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(msg=f"current ex {ex}")
    msg_ex  = update.effective_message.text
    newexmsg = msg_ex.split(" ")
    newex=newexmsg[1]
    typeex=newexmsg[0]
    try:
        if (typeex=="/cex"):
            SearchCEXResults= await SearchCEX(newex,testmode)
            CEX_name = SearchCEXResults[0]['name']
            CEX_test_mode = testmode
            res = await LoadExchange(CEX_name,CEX_test_mode)
            response = f"CEX is {ex}"
        elif (typeex=="/dex"):
            SearchDEXResults= await SearchDEX(newex,testmode)
            DEX_name= SearchDEXResults[0]['name']
            DEX_test_mode= testmode
            logger.info(msg=f"DEX_test_mode: {DEX_test_mode}")
            logger.info(msg=f"DEX_name: {DEX_name}")
            res = await LoadExchange(DEX_name,DEX_test_mode)
            logger.info(msg=f"res: {res}")
            response = f"DEX is {DEX_name}"
        await send(update,response)
    except Exception as e:
        await HandleExceptions(e)
##======TG COMMAND Test mode switch ======
async def TestModeSwitch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global testmode
    if (testmode=="False"):
        testmode="True"
    else:
        testmode="False"
    message=f"Sandbox is {testmode}"
    await send(update,message)
##======== DB START ===============
DBURL=os.getenv("DBURL")
if DBURL==None:
    logger.info(msg=f"No remote DB")
else:
    outfile = os.path.join('./config', 'db.json')
    response = requests.get(DBURL, stream=True)
    logger.info(msg=f"{response}")
    with open(outfile,'wb') as output:
        output.write(response.content)

if not os.path.exists(db_path):
    logger.info(msg=f"contingency process DB")
    failsafe=True
    ex='tbd'
    db_path=contingency_db_path
    try:
        load_dotenv(dotenv_path)
        TG_TK = os.getenv("TG_TK")
        TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
    except Exception as e:
        logger.error("no TG TK")
        sys.exit()

if os.path.exists(db_path):
    logger.info(msg=f"Existing DB")
    failsafe=False
    try:
        db = TinyDB(db_path)
        q = Query()
        globalDB = db.table('global')
        env = globalDB.all()[0]['env']
        ex = globalDB.all()[0]['defaultex']
        testmode = globalDB.all()[0]['defaulttestmode']
        logger.info(msg=f"Env {env} ex {ex}")
        telegramDB = db.table('telegram')
        cexDB = db.table('cex')
        dexDB = db.table('dex')
        tg=telegramDB.search(q.platform==env)
        TG_TK = tg[0]['token']
        TG_CHANNEL_ID = tg[0]['channel']
        TG_WBHK_PORT=tg[0]['port']
        TG_WBHK_SECRET=tg[0]['secret_token']
        TG_WBHK_PVTKEY=tg[0]['key']
        TG_WBHK_CERT=tg[0]['cert']
        TG_WBHK_URL=tg[0]['webhook_url']
        cexdb=cexDB.all()
        dexdb=dexDB.all()
        if (TG_TK==""):
            logger.error(msg=f"no TG TK")
            sys.exit()
    except Exception:
        logger.warning(msg=f"error with existing db file {db_path}")
##======== APPRISE Setup ===============
apobj = apprise.Apprise()
apobj.add('tgram://' + str(TG_TK) + "/" + str(TG_CHANNEL_ID))
##========== startup message ===========
async def post_init(application: Application):
    await LoadExchange(ex,testmode)
    logger.info(msg=f"Bot is online")
    await application.bot.send_message(TG_CHANNEL_ID, f"Bot is online {version}", parse_mode=constants.ParseMode.HTML)
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
        LibCheck()
#Starting Bot TPB
        application = Application.builder().token(TG_TK).post_init(post_init).build()

#TPBMenusHandlers
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
        application.add_handler(MessageHandler(filters.Regex('/p'), price_command))
        application.add_handler(MessageHandler(filters.Regex('/c'), coin_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), TradingSwitch))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), SwitchEx))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), TestModeSwitch))
        application.add_handler(MessageHandler(filters.Regex('/g'), token_command))
        #application.add_error_handler(error_handler)
        # application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
        # application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))
        #application.add_handler(MessageHandler(filters.Regex('/restart'), restart_command))

#Run the bot
        webhook=False
        if (webhook):
            logger.info(msg=f"Webhook initiation")
            application.run_webhook(
                listen='0.0.0.0',
                port=TG_WBHK_PORT,
                secret_token=TG_WBHK_SECRET,
                key=TG_WBHK_PVTKEY,
                cert=TG_WBHK_CERT,
                webhook_url=TG_WBHK_URL
            )
        else:
            application.run_polling()

    except Exception as e:
        logger.info("Bot failed to start. Error: " + str(e))

if __name__ == '__main__':
    main()
