##=============== VERSION =============
TTversion="🪙TT Beta 1.03.10"
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
load_dotenv()  # .env loading 
db_path = './config/db.json'

#===================
global ex
exchanges = {}
trading=True
testmode="True"
headers = { "User-Agent": "Mozilla/5.0" }
cg = CoinGeckoAPI()

#===================
fullcommandlist = """
<code>/bal</code>
<code>/cex kraken</code> <code>buy btc/usdt sl=1000 tp=20 q=1%</code> <code>/q btc/usdt</code>
<code>/cex binance</code> <code>buy btcusdt sl=1000 tp=20 q=1%</code> <code>/q btcusdt</code>
<code>/dex pancake</code> <code>buy cake</code> <code>/q BTCB</code>
<code>/trading</code>
<code>/testmode</code>"""
menuhelp = f"{TTversion} \n {fullcommandlist}"

#========== Common Functions =============
def verify_import_library():
    logger.info(msg=f"{TTversion}")
    logger.info(msg=f"Python {sys.version}")
    logger.info(msg=f"TinyDB {tinydb.__version__}")
    logger.info(msg=f"TPB {telegram.__version__}")
    logger.info(msg=f"CCXT {ccxt.__version__}")
    logger.info(msg=f"Web3 {web3.__version__}")
    logger.info(msg=f"apprise {apprise.__version__}")
    return

##===========DB Functions
async def add_tg_db_command(s1, s2, s3):
    if len(telegram_db.search(q.token == s1)):
        logger.info(msg=f"token is already setup")
    else:
        telegram_db.insert({"token": s1, "channel": s2, "platform": s3})

async def add_cex_db_command(s1, s2, s3, s4, s5, s6, s7):
    if len(cex_db.search(q.api == s2)):
        logger.info(msg=f"EX exists in DB")
    else:
        cex_db.insert({
            "name": s1,
            "api": s2,
            "secret": s3,
            "password": s4,
            "testmode": s5,
            "ordertype": s6,
            "defaultType": s7})

async def add_dex_db_command(s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11):
    if len(dex_db.search(q.name == s1)):
        logger.info(msg=f"EX exists in DB")
    else:
        dex_db.insert({
            "name": s1,
            "walletaddress": s2,
            "privatekey": s3,
            "version": s4,
            "networkprovider": s5,
            "router": s6,
            "testmode": s7,
            "tokenlist": s8,
            "abiurl": s9,
            "abiurltoken": s10,
            "basesymbol": s11})

async def drop_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"db dropped")
    db.drop_tables()

async def show_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(msg=f"display db")
    message = f" db extract: \n {db.all()}"
    await send(update, message)

#=========Exchange Functions
async def search_cex(ex_name, ex_mode):
    if type(ex_name) is str:
        query1 = ((q.name == ex_name) & (q['testmode'] == ex_mode))
        result_cex_db = cex_db.search(query1)
        if (len(str(result_cex_db)) >= 1):
            return result_cex_db
    elif type(string1) is not str:
        try:
            query1 = ((q.name == ex_name.name.lower()) & (q['testmode'] == ex_mode))
            result_cex_db = cex_db.search(query1)
            if (len(str(result_cex_db)) == 1):
                return result_cex_db
            else:
                return
        except Exception as e:
            await handle_exception(e)
            return
    else:
        return

async def search_dex(ex_name, ex_mode):
    try:
        query = ((q.name == ex_name) & (q['testmode'] == ex_mode))
        result_dex_db = dex_db.search(query)
        if (len(str(result_dex_db)) >= 1):
            return result_dex_db
        else:
            return
    except Exception as e:
        await handle_exception(e)
        return

async def search_exchange(ex_name, ex_mode):
    try:
        if (isinstance(ex_name, str)):
            check_cex = await search_cex(ex_name, ex_mode)
            check_dex = await search_dex(ex_name, ex_mode)
            if (check_cex != None):
                if(len(str(check_cex)) >= 1):
                    return check_cex[0]['name']
            elif (len(str(check_dex)) >= 1):
                return check_dex[0]['name']
        elif not (isinstance(ex_name, web3.main.Web3)):
            check_cex = await search_cex(ex_name.id, ex_mode)
            return check_cex[0]['name']
        elif (isinstance(ex_name, web3.main.Web3)):
            check_dex = await search_dex(ex_name, ex_mode)
            return name
        else:
            return
    except Exception as e:
        await handle_exception(e)
        return

async def load_exchange(exchangeid, mode):
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
   # global quoter_instance
   # global quoter_instanceabi
    global platform
    global chainId
    if (failsafe):
        ex = Web3(Web3.HTTPProvider('https://ethereum.publicnode.com'))
        return
    logger.info(msg=f"Setting up {exchangeid}")
    check_cex= await search_cex(exchangeid,mode)
    check_dex= await search_dex(exchangeid,mode)
    if (check_cex):
        newex=check_cex
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
                #logger.info(msg=f"ex: {ex}")
                #ex.verbose = True
                #logger.info(msg=f"markets: {markets}")
                return ex
            else:
                markets=ex.loadMarkets ()
                #logger.info(msg=f"ex: {ex}")
                return ex

        except Exception as e:
            await handle_exception(e)
    elif (check_dex):
        newex= check_dex
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
        chainId=newex[0]['chainId']
        ex = Web3(Web3.HTTPProvider('https://'+networkprovider))
        router_instanceabi= await fetch_abi_dex(router) #Router ABI
        router_instance = ex.eth.contract(address=ex.to_checksum_address(router), abi=router_instanceabi) #ContractLiquidityRouter
        if (version=="v3"):
            quoter_instanceabi= await fetch_abi_dex('0x61fFE014bA17989E743c5F6cB21bF9697530B21e') #Quoter ABI
            quoter_instance = ex.eth.contract(address=ex.to_checksum_address('0x61fFE014bA17989E743c5F6cB21bF9697530B21e'), abi=quoter_instanceabi) #ContractLiquidityQuoter
        try:
            ex.net.listening
            logger.info(msg=f"connected to {ex}")
            return name
        except e as Exception:
            await handle_exception(e)
    else:
        return

def search_tokenlist(parsedJson, name):
    #logger.info(msg=f"name {name} chainId {chainId}")
    #logger.info(msg=f"parsedJson {parsedJson}")
    for entry in parsedJson:
        if name == entry ['symbol']:
            logger.info(msg=f"entry{entry ['symbol']}{entry ['chainId']} {entry ['address']}")
            if int(chainId) == entry ['chainId']:
                return entry ['address']


async def search_contract_dex(symb):
    try:
        url = requests.get(tokenlist)
        text = url.text
        token_list = json.loads(text)['tokens']
        symb=symb.upper()
        try:
            symbolcontract=search_tokenlist(token_list,symb)
            logger.info(msg=f"symbolcontract {symbolcontract}")
            if symbolcontract != None:
                return symbolcontract
            else:
                msg=f"{symb} does not exist in {tokenlist}"
                await handle_exception(msg)
                return
        except Exception as e:
            await handle_exception(e)
            return
    except Exception as e:
        #logger.info(msg=f"error {search_contract_dex} {symb}")
        await handle_exception(e)
        return

async def fetch_abi_dex(addr):
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
        await handle_exception(e)

#ORDER PARSER
def convert(s):
    li = s.split(" ")
    try:
        m_dir= li[0]
    except (IndexError, TypeError):
        e=f"{s} no direction"
        logger.error(msg=f"{e}")
        handle_exception(e)
        return
    try:
        m_symbol=li[1]
    except (IndexError, TypeError):
        e=f"{s} no symbol"
        logger.error(msg=f"{e}")
        handle_exception(e)
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
        m_q=5
    order=[m_dir,m_symbol,m_sl,m_tp,m_q]
    logger.info(msg=f"order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
    return order

async def parse_message (message):
    parsed_message = message.split(" ")
    filter_lst_order = ['buy']
    filter_lst_quote = ['/q']
    if [ele for ele in filter_lst_order if(ele in parsed_message)]: 
      logger.info(msg=f"case 1: {message}")
    
#========== Order function
async def send_order(s1,s2,s3,s4,s5):
    try:
      if not isinstance(ex,web3.main.Web3):
        logger.info(msg=f"order: {s1} {s2} {s3} {s4} {s5}")
        response = await send_order_cex(s1,s2,s3,s4,s5)
      elif (isinstance(ex,web3.main.Web3)):
        response = await send_order_dex(s1,s2,s3,s4,s5)
      return response
    except Exception as e:
      await handle_exception(e)
      return

async def send_order_cex(s1,s2,s3,s4,s5):
    try:
        bal = ex.fetch_free_balance()
        bal = {k: v for k, v in bal.items() if v is not None and v>0}
        if (len(str(bal))):
            m_price = float(ex.fetchTicker(f'{s2}').get('last'))
            totalusdtbal = ex.fetchBalance()['USDT']['free']
            amountpercent=((totalusdtbal)*(float(s5)/100))/float(m_price) # % of bal
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
                response+= f"\n➕ Size: {amount}\n⚫️ Entry: {price}\nℹ️ {orderid}\n🗓️ {timestamp}"
                return response
            except Exception as e:
                await handle_exception(e)
                return
    except Exception as e:
        await handle_exception(e)
        return

async def verify_gas_dex():
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



async def fetch_token_price(s1):
    try:
        coininfo=cg.search(query=s1) 
        for i in coininfo['coins']:
            fetch_tokeninfo=i['symbol']
            if (fetch_tokeninfo==s1):
                # logger.info(msg=f"{i['api_symbol']}")
                coininfo=cg.get_coin_by_id(id=i['api_symbol'])
                coinplatform=coininfo['asset_platform_id']
                # logger.info(msg=f"coinplatform {coinplatfrom}")
                coinprice=coininfo['market_data']['current_price']['usd']
                # logger.info(msg=f"coingeckoprice {coinprice}")
                coinsymbol=coininfo['symbol']
                response = f'coingecko info: {coinsymbol} {coinprice} USD on {coinplatform}'
                logger.info(msg=f"{response}")
                return coinprice
    except Exception:
        return

async def sign_dex_transaction(contract_tx):
    try:
        if (version=='v2'):
            tx_params = {
                'from': walletaddress,
                'gas': int(gasLimit),
                'gasPrice': ex.to_wei(gasPrice,'gwei'),
                'nonce': ex.eth.get_transaction_count(walletaddress),
            }
            tx = contract_tx.build_transaction(tx_params)
            signed = ex.eth.account.sign_transaction(tx, privatekey)
            raw_tx = signed.rawTransaction
            return ex.eth.send_raw_transaction(raw_tx)
        elif (version=="v3"):
            tx_params = {
                'from': walletaddress,
                'gas': int(gasLimit),
                'gasPrice': ex.to_wei(gasPrice,'gwei'),
                'nonce': ex.eth.get_transaction_count(walletaddress),
            }
            tx = contract_tx.build_transaction(tx_params)
            signed = ex.eth.account.sign_transaction(tx, privatekey)
            raw_tx = signed.rawTransaction
            return ex.eth.send_raw_transaction(raw_tx)
        elif (version=="1inch"):
            tx_params = {
                'nonce': ex.eth.get_transaction_count(walletaddress),
                'gas': int(gasLimit),
                'gasPrice': ex.to_wei(gasPrice,'gwei'),
            }
            tx = contract_tx.build_transaction(tx_params)
            logger.info(msg=f"tx {tx}")
            signed = ex.eth.account.sign_transaction(tx, privatekey)
            logger.info(msg=f"signed {signed}")
            raw_tx = signed.rawTransaction
            logger.info(msg=f"raw_tx {raw_tx}")
            return ex.eth.send_raw_transaction(raw_tx)
        else:
            return
    except Exception:
        return

async def send_order_dex(s1,s2,s3,s4,s5):
    try:
        if (s1=="BUY"):
            token_out_symbol=basesymbol
            token_in_symbol=s2
        else:
            token_out_symbol=s2
            token_in_symbol=basesymbol
        token_out_address=ex.to_checksum_address(await search_contract_dex(token_out_symbol))
        token_out_abi= await fetch_abi_dex(token_out_address) 
        token_out_contract = ex.eth.contract(address=token_out_address, abi=token_out_abi)
        token_in_address= ex.to_checksum_address(await search_contract_dex(token_in_symbol))
        OrderPath=[token_out_address, token_in_address]
        token_out_balance=token_out_contract.functions.balanceOf(walletaddress).call()
        if (token_out_balance <=0):
          return
        logger.info(msg=f"token_out_balance {token_out_balance}")
        token_out_decimals=token_out_contract.functions.decimals().call()
        slippage=1
        if (s1=="SELL"):
            token_out_amount = (token_out_balance)/(10 ** token_out_decimals) #SELL all token in case of sell order
            response = f"⬇️ {s2}"
            token_out_quote= await fetch_token_price(token_out_symbol)
        else:
            token_out_amount = ((token_out_balance)/(10 ** token_out_decimals))*(float(s5)/100) #buy %p ercentage
            response = f"⬆️ {s2}"
            token_in_quote= await fetch_token_price(token_in_symbol)
        i_OrderAmount=(ex.to_wei(token_out_amount,'ether'))
        OrderAmount = i_OrderAmount
        # deadline = ex.eth.getBlock("latest")["timestamp"] + 3600
        deadline = (int(time.time()) + 1000000)
        if (version=='v2'):
            approvalcheck = token_out_contract.functions.allowance(ex.to_checksum_address(walletaddress), ex.to_checksum_address(router)).call()
            logger.info(msg=f"approvalcheck {approvalcheck}")
            if (approvalcheck==0):
                maxamount = (ex.to_wei(2**64-1,'ether'))
                approval_TX = token_out_contract.functions.approve(ex.to_checksum_address(router), maxamount)
                ApprovaltxHash = await sign_dex_transaction(approval_TX)
                logger.info(msg=f"Approval {str(ex.to_hex(ApprovaltxHash))}")
                time.sleep(10) #wait approval
            OptimalOrderAmount  = router_instance.functions.getOutputAmount(OrderAmount, OrderPath).call()
            MinimumAmount = int(OptimalOrderAmount[1] *0.98)# max 2% slippage
            swap_TX = router_instance.functions.swapExactTokensForTokens(OrderAmount,MinimumAmount,OrderPath,walletaddress)
            tx_token = await sign_dex_transaction(swap_TX)
        elif (version=="1inch"):
            logger.info(msg=f"1inch processing")
            logger.info(msg=f"{OrderAmount}")
            endpoint=f'https://api.1inch.exchange/v5.0/{chainId}/'
            approval_URL = f"{endpoint}approve/transaction?tokenAddress={tokenToSell}"
            logger.info(msg=f"{approval_URL}")
            approval_response = requests.get(approval_URL)
            approval= approval_response.json()
            logger.info(msg=f"approval {approval}")
            swap_url = f"{endpoint}swap?fromTokenAddress={token_out_address}&toTokenAddress={token_in_address}&amount={OrderAmount}&fromAddress={walletaddress}&slippage={slippage}"
            logger.info(msg=f"swap_url {swap_url}")
            swap_response = requests.get(swap_url)
            logger.info(msg=f"swap_response {swap_response}")
            swap_raw = swap_response.json()
            logger.info(msg=f"swap_raw {swap_raw}")
            # tx_token = await sign_dex_transaction(swap_raw)
            # logger.info(msg=f"tx_token {tx_token}")
            swap_raw['nonce'] = ex.eth.get_transaction_count(walletaddress)
            swap_raw['gas']= int(gasLimit)
            swap_raw['gasPrice']= ex.to_wei(gasPrice,'gwei')
            logger.info(msg=f"swap_raw updated {swap_raw}")
            signed = ex.eth.account.sign_transaction(swap_raw, privatekey)
            logger.info(msg=f"signed {signed}")
            raw_tx = signed.rawTransaction
            tx_token= ex.eth.send_raw_transaction(raw_tx)
        elif (version=="v3"):
            logger.info(msg=f"v3 support")
            return
            ####Uniswap V3 contrac function prep
            # fee=int(3000)
            # sqrt_price_limit_x96 = 0
            # #OptimalOrderAmount  = quoter_instance.functions.getSwapQuote(tokenToSell, OrderAmount, tokenToBuy).call()
            # #MinimumAmount=int(OptimalOrderAmount[1] *0.98)# max 2% slippage
            # swap_TX=router_instance.functions.addOrder(tokenToBuy,OrderAmount,tokenToSell,OrderAmountfee)
            # tx_token = await sign_dex_transaction(swap_TX)
        elif (version =="limitorder"):
            logger.info(msg=f"limitorder processing")
            return
            #TBD
        else:
            return
        txHash = str(ex.to_hex(tx_token))
        checkTransactionSuccessURL = abiurl + "?module=transaction&action=gettxreceiptstatus&txhash=" + txHash + "&apikey=" + abiurltoken
        checkTransactionRequest = requests.get(url=checkTransactionSuccessURL,headers=headers)
        txResult = checkTransactionRequest.json()['status']
        #await verify_gas_dex()
        txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
        fetch_token_price=coinprice
        gasUsed=txHashDetail['gasUsed']
        txtimestamp=datetime.now()
        if(txResult == "1"):
            response+= f"\n➕ Size: {round(ex.from_wei(OrderAmount, 'ether'),5)}\n⚫️ Entry: {fetch_token_price}USD \nℹ️ {txHash}\n⛽️ {gasUsed}\n🗓️ {txtimestamp}"
            logger.info(msg=f"{response}")
            return response     
    except Exception as e:
        await handle_exception(e)
        return

async def fetch_tokeninfo(token):
    global token_price
    global token_info
    #asset_platforms = cg.get_asset_platforms()
    #logger.info(msg=f"cg.get_asset_platforms {asset_platforms}")
    try:
        coininfo=cg.get_coin_by_id(id=token) 
        coinplatform=coininfo['asset_platform_id']
        coindescription=coininfo['description']['en']
        coinprice=coininfo['market_data']['current_price']['usd']
        coinsymbol=coininfo['symbol']
        coinlink='https://www.coingecko.com/en/coins/'+coininfo['symbol']
        response = f'{coinsymbol} {coinprice} USD \n{coindescription}\n{coinlink}'
        logger.info(msg=f"{response}")   
        return response
    except Exception:
        return
       
async def fetch_tokeninfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    symbol=parsed_message[1].upper()
    try:
        coininfo=cg.search(query=symbol) 
        #logger.info(msg=f"coininfo {coininfo}")
        for i in coininfo['coins']:
            results_search_coin = i['symbol']
            if (results_search_coin==symbol):
                logger.info(msg=f"Pass")
                logger.info(msg=f"{i['api_symbol']}")
                coininfo=cg.get_coin_by_id(id=i['api_symbol'])
                coinplatform=coininfo['asset_platform_id']
                logger.info(msg=f"coinplatfrom {coinplatfrom}")
                coinprice=coininfo['market_data']['current_price']['usd']
                logger.info(msg=f"coinprice {coinprice}")
                coinsymbol=coininfo['symbol']
                response = f'{coinsymbol} {coinprice} USD on {coinplatform}'
                logger.info(msg=f"{response}")
    except Exception as e:
        return

async def verify_latency_ex():
    if not isinstance(ex,web3.main.Web3):
        symbol = 'BTC/USDT'
        results = []
        num_iterations = 5
        for i in range(0, num_iterations):
            started = ex.milliseconds()
            orderbook = ex.fetch_order_book(symbol)
            ended = ex.milliseconds()
            elapsed = ended - started
            #logger.info(msg=f"elapsed {elapsed}")
            results.append(elapsed)
        rtt = int(sum(results) / len(results))
        response = rtt
    elif (isinstance(ex,web3.main.Web3)):
        #logger.info(msg=f"networkprovider {networkprovider}")
        response = round(ping(networkprovider, unit='ms'),3)
    return response

#=========== Send function
async def send (self, messaging):
    try:
        await self.effective_chat.send_message(f"{messaging}", parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await handle_exception(e)
#========== notification function
async def notify(messaging):
#=APPRISE Setup
  apobj = apprise.Apprise()
  if (telegram_token != None):
    apobj.add('tgram://' + str(telegram_token) + "/" + str(telegram_channel_id))
    try:
        apobj.notify(body=messaging)
    except Exception as e:
        logger.error(msg=f"error: {e}")
  else:
    logger.error(msg=f"not delivered {messaging}")
#======= error handling
async def handle_exception(e) -> None:
    try:
        msg=f"error:"
        logger.error(msg=f"error: {e}")
    except KeyError:
        msg=f"DB content error"
    except IndexError:
        msg=f"Parsing error"
    except telegram.error:
        msg=f"telegram error"
    except ConnectionError:
        msg=f'Could not connect to RPC'
    except Web3Exception.error:
        msg=f"web3 error"
    except ccxt.base.errors:
        msg=f"CCXT error"
    except ccxt.NetworkError:
        msg=f"Network error"
    except ccxt.ExchangeError:
        msg=f"Exchange error"
    except Exception:
        msg=f"{e}"
    message=f"⚠️ {msg} {e}"
    logger.error(msg=f"{message}")
    await notify(message)
##======== END OF FUNCTIONS ============

##============TG COMMAND================
##====view help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r_ping = await verify_latency_ex()
    msg= f"Environment: {env} Ping: {r_ping}ms\nExchange: {await search_exchange(ex,testmode)} Sandbox: {testmode}\n{menuhelp}"
    await send(update,msg)
##====restart ====
async def restart_command(application: Application, update: Update) -> None:
    logger.info(msg=f"restarting ")
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])
##====stop =======
async def stop_command(self) -> None:
  if self.application is None or self.application.updater is None:
    return
  await self.application.updater.stop()
  await self.application.stop()
  await self.application.shutdown()
        
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
        await handle_exception(e)

#===order parsing  ======
async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message = update.effective_message.text
    uppercased_message = channel_message.upper()
    filter_lst = ['BUY', 'SELL']
    msg=""
    if [ele for ele in filter_lst if(ele in uppercased_message)]:
        if (trading==False):
            message="TRADING DISABLED"
            await send(update,message)
        else:
            print('echo')
            try:
                order_m = convert(uppercased_message)
                m_dir= order_m[0]
                m_symbol=order_m[1]
                m_sl=order_m[2]
                m_tp=order_m[3]
                m_q=order_m[4]
                logger.info(msg=f"Processing order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
                res=await send_order(m_dir,m_symbol,m_sl,m_tp,m_q)
                if (res!= None):
                    response=f"{res}"
                    await send(update,response)
            except Exception as e:
                await handle_exception(e)
                return
##======TG COMMAND view price ===========
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    filter_lst = ['/p']
    if [ele for ele in filter_lst if(ele in parsed_message)]:
        symbol=parsed_message[1]
        try:
            if not (isinstance(ex,web3.main.Web3)):
                price= ex.fetch_ticker(symbol.upper())['last']
                response=f"₿ {symbol} @ {price}"
            elif (isinstance(ex,web3.main.Web3)):
                if(await search_contract_dex(symbol) != None):
                    symbol_to_quote = ex.to_checksum_address(await search_contract_dex(symbol))
                    logger.info(msg=f"token {symbol_to_quote}")
                    tokenToSell='USDT'
                    basesymbol=ex.to_checksum_address(await search_contract_dex(tokenToSell))
                    if(symbol_to_quote != None):
                        fetch_tokeninfo=cg.get_coin_info_from_contract_address_by_id(id=platform,contract_address=symbol_to_quote)
                        fetch_token_price=fetch_tokeninfo['market_data']['current_price']['usd']
                        amountTosell=1
                        endpoint=f'https://api.1inch.exchange/v5.0/{chainId}/'
                        quote_url = f"{endpoint}quote?fromTokenAddress={symbol_to_quote}&toTokenAddress={basesymbol}&amount={amountTosell}"
                        quote_response = requests.get(quote_url)
                        quote = quote_response.json()
                        estimatedGas = quote['estimatedGas']
                        toTokenAmount = quote['toTokenAmount']
                        response=f"₿ {symbol_to_quote}\n{symbol} @ {toTokenAmount} (1inch - live) or {fetch_token_price} (gecko)"
                        await send(update,response)
                        #version2 router command
                            # price = router_instance.functions.getAmountsOut(1, [symbol_to_quote,basesymbol]).call()[1]
                            # logger.info(msg=f"price {price}")
                            # response=f"₿ {symbol_to_quote}\n{symbol} @ {(price)} or {fetch_token_price}"
                            #await DEX_fetch_tokeninfo(symbol)
        except Exception as e:
            await handle_exception(e)
            return
##======TG COMMAND coin info  ===========
async def coininfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    symbol=parsed_message[1]
    try:
        response=await fetch_tokeninfo(symbol)
        await send(update,response)
    except Exception as e:
        await handle_exception(e)
        return
##====TG COMMAND Trading switch  ========
async def trading_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trading
    if (trading==False):
        trading=True
    else:
        trading=False
    message=f"Trading is {trading}"
    await send(update,message)
##====TG COMMAND CEX DEX switch =========
async def switch_exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(msg=f"current ex {ex}")
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    newex=parsed_message[1]
    typeex=parsed_message[0]
    try:
        if (typeex=="/cex"):
            results_search_cex= await search_cex(newex,testmode)
            CEX_name = results_search_cex[0]['name']
            CEX_test_mode = testmode
            res = await load_exchange(CEX_name,CEX_test_mode)
            response = f"CEX is {ex}"
        elif (typeex=="/dex"):
            results_search_dex= await search_dex(newex,testmode)
            DEX_name= results_search_dex[0]['name']
            DEX_test_mode= testmode
            logger.info(msg=f"DEX_test_mode: {DEX_test_mode}")
            logger.info(msg=f"DEX_name: {DEX_name}")
            res = await load_exchange(DEX_name,DEX_test_mode)
            logger.info(msg=f"res: {res}")
            response = f"DEX is {DEX_name}"
        await send(update,response)
    except Exception as e:
        await handle_exception(e)
##======TG COMMAND Test mode switch ======
async def testmode_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global testmode
    if (testmode=="False"):
        testmode="True"
    else:
        testmode="False"
    message=f"Sandbox is {testmode}"
    await send(update,message)
    
##======== DB START ===============
db_url=os.getenv("DB_URL")
if db_url==None:
    logger.info(msg=f"No remote DB")
else:
    outfile = os.path.join('./config', 'db.json')
    response = requests.get(db_url)
    with open(outfile,'w') as output:
        output.write(response.content)
        logger.info(msg=f"copied the remote DB")

        
if not os.path.exists(db_path):
    logger.info(msg=f"contingency process DB")
    failsafe=True
    ex='tbd'
    contingency_db_path = './config/sample_db.json'
    db_path=contingency_db_path
    try:
        telegram_token = os.getenv("TG_TK")
        telegram_channel_id = os.getenv("TG_CHANNEL_ID")
    except Exception as e:
        logger.error("no telegram token")
        time.sleep(1000)

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
        telegram_db = db.table('telegram')
        cex_db = db.table('cex')
        dex_db = db.table('dex')
        tg=telegram_db.search(q.platform==env)
        telegram_token = tg[0]['token']
        telegram_channel_id = tg[0]['channel']
        telegram_webhook_port=tg[0]['port']
        telegram_webhook_secret=tg[0]['secret_token']
        telegram_webhook_privatekey=tg[0]['key']
        telegram_webhook_certificate=tg[0]['cert']
        telegram_webhook_url=tg[0]['webhook_url']
        if (telegram_token==""):
            logger.error("no TG TK")
            logger.warning(msg=f"Failover process")
            time.sleep(1000)
    except Exception:
        logger.warning(msg=f"error with existing db file {db_path}")
        
##========== startup message ===========
async def post_init(application: Application):
    message=f"Bot is online {TTversion}"
    await load_exchange(ex,testmode)
    logger.info(msg=f"{message}")
    await application.bot.send_message(telegram_channel_id, message, parse_mode=constants.ParseMode.HTML)
#===========bot error handling ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e=f"{tb_trim}"
    await handle_exception(e)

#================== BOT =================
def main():
    try:
        verify_import_library()
#Starting Bot TPB
        application = Application.builder().token(telegram_token).post_init(post_init).build()

#TPBMenusHandlers
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
        application.add_handler(MessageHandler(filters.Regex('/q'), quote_command))
        application.add_handler(MessageHandler(filters.Regex('/c'), coininfo_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), trading_switch_command))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), switch_exchange_command))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), testmode_switch_command))
        application.add_handler(MessageHandler(filters.Regex('/g'), fetch_tokeninfo_command))
        application.add_handler(MessageHandler(filters.Regex('/restart'), restart_command))
        application.add_error_handler(error_handler)
        # application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
        # application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))

#Run the bot
        webhook=False
        if (webhook):
            logger.info(f"Webhook start")
            try:
              application.run_webhook(
                listen='0.0.0.0',
                port=telegram_webhook_port,
                secret_token=telegram_webhook_secret,
                #key=telegram_webhook_privatekey,
                #cert=telegram_webhook_certificate,
                webhook_url=telegram_webhook_url
              )
            except Exception as e:
             logger.info("Bot failed to start. Error: " + str(e))
             #application.run_polling(drop_pending_updates=True)
        else:
         application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.info("Bot failed to start. Error: " + str(e))

        
if __name__ == '__main__':
    main()
