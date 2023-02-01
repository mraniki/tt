##=============== VERSION =============
TTversion="🪙TT Beta 1.03.21"
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
#===================
ex = "pancake"
chainId = 56
exchanges = {}
bot_trading_switch=True
ex_test_mode="True"

#=======API endpoint
headers = { "User-Agent": "Mozilla/5.0" }
ex_gecko_api = CoinGeckoAPI()
dex_1inch_api = f"https://api.1inch.exchange/v5.0/{chainId}"
dex_cow_api = f"https://api.cow.fi/mainnet"
dex_guru_api = f"https://api.dev.dex.guru/v1/{chainId}/?api-key="

#=======TG command
fullcommandlist = """
<code>/bal</code>
<code>/cex kraken</code>
order sample
<code>buy btc/usdt sl=1000 tp=20 q=1%</code>
<code>/dex pancake</code> <code>buy cake</code>
quote sample
<code>/q BTCB</code> <code>/q WBTC</code> <code>/q btc/usdt</code>
other commands
<code>/trading</code> <code>/testmode</code>"""
bot_menu_help = f"{TTversion} \n {fullcommandlist}"

filter_order = ['BUY', 'SELL']
filter_quote = ['/q', '/p']

#========== Common Functions =============

def verify_import_library():
    logger.info(msg=f"{TTversion}")
    logger.info(msg=f"Python {sys.version}")
    logger.info(msg=f"TinyDB {tinydb.__version__}")
    logger.info(msg=f"TPB {telegram.__version__}")
    logger.info(msg=f"CCXT {ccxt.__version__}")
    logger.info(msg=f"Web3 {web3.__version__}")
    logger.info(msg=f"apprise {apprise.__version__}")

##===========DB Functions

async def add_tg_db_command(s1, s2, s3):
    if len(bot_db.search(q.token == s1)):
        logger.info(msg=f"token is already setup")
    else:
        bot_db.insert({"token": s1, "channel": s2, "platform": s3})

async def add_cex_db_command(s1, s2, s3, s4, s5, s6, s7):
    if len(cex_db.search(q.api == s2)):
        logger.info(msg=f"EX exists in DB")
    else:
        cex_db.insert({"name": s1,
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
        dex_db.insert({"name": s1,
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

####Search related Functions

#PARSER
async def convert(s):
    # li = s.split(" ")
    # try:
    #     m_dir= li[0]
    # except (IndexError, TypeError):
    #     e=f"{s} no direction"
    #     logger.error(msg=f"{e}")
    #     handle_exception(e)
    #     return
    # try:
    #     m_symbol=li[1]
    # except (IndexError, TypeError):
    #     e=f"{s} no symbol"
    #     logger.error(msg=f"{e}")
    #     handle_exception(e)
    #     return
    # try:
    #     m_sl=li[2][3:7]
    # except (IndexError, TypeError):
    #     logger.warning(msg=f"{s} no sl")
    #     m_sl=0
    # try:
    #     m_tp=li[3][3:7]
    # except (IndexError, TypeError):
    #     logger.warning(msg=f"{s} no tp")
    #     m_tp=0
    # try:
    #     m_q=li[4][2:-1]
    # except (IndexError, TypeError):
    #     logger.warning(msg=f"{s} no size default to 10 %")
    #     m_q=5
    # order=[m_dir,m_symbol,m_sl,m_tp,m_q]
    # logger.info(msg=f"order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
    # return order
    try:
        parts = s.split(" ")
        direction = parts[0]
        symbol = parts[1]
        stop_loss = int(parts[2][3:7]) if len(parts) >= 3 else 0
        take_profit = int(parts[3][3:7]) if len(parts) >= 4 else 0
        quantity = int(parts[4][2:-1]) if len(parts) >= 5 else 5
        return [direction, symbol, stop_loss, take_profit, quantity]
    except (IndexError, TypeError, ValueError) as e:
        logger.error(f"Error parsing order string '{s}': {e}")
        return None

#parserv2
async def parse_message (message):
    parsed_message = message.split(" ")
    filter_lst_order = ['buy']
    filter_lst_quote = ['/q']
    if [ele for ele in filter_lst_order if(ele in parsed_message)]:
      logger.info(msg=f"case 1: {message}")

#exchangerater
async def request_eur(self):
    url = 'https://openexchangerates.org/api/latest.json'
    params = {'app_id':openexchange_api_key, 'symbols':'EUR', 'base':'USD', 'prettyprint':False}
    r = requests.get(url, params=params)
    try:
        d = json.loads(r.text)
        self.latest_eur = float(d['rates']['EUR'])
            #print('eur updated')
    except:
        logger.info(msg=f"error getting EUR rate")
        self.latest_eur = 1 #reasonable rate


#=========Exchange Functions
async def search_cex(ex_name, ex_test_mode):
    if (isinstance(ex_name, str)):
        query1 = ((q.name == ex_name) & (q['testmode'] == ex_test_mode))
        result_cex_db = cex_db.search(query1)
        logger.info(msg=f"result_cex_db {result_cex_db}")
        if (len(str(result_cex_db)) >= 1):
            return result_cex_db
        if not (isinstance(ex_name, str)):
            try:
                query1 = ((q.name == ex_name.name.lower()) & (q['testmode'] == ex_test_mode))
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

async def search_dex(ex_name, ex_test_mode):
    try:
        query = ((q.name == ex_name) & (q['testmode'] == ex_test_mode))
        result_dex_db = dex_db.search(query)
        logger.info(msg=f"result_dex_db {result_dex_db}")
        if (len(str(result_dex_db)) >= 1):
            return result_dex_db
        else:
            return
    except Exception as e:
        await handle_exception(e)
        return

async def search_exchange(ex_name, ex_test_mode):
    try:
        if (isinstance(ex_name, str)):
            check_cex = await search_cex(ex_name, ex_test_mode)
            check_dex = await search_dex(ex_name, ex_test_mode)
            if (check_cex is not None):
                if(len(str(check_cex)) >= 1):
                    return check_cex[0]['name']
            elif (len(str(check_dex)) >= 1):
                return check_dex[0]['name']
        elif not (isinstance(ex_name, web3.main.Web3)):
            check_cex = await search_cex(ex_name.id, ex_test_mode)
            return check_cex[0]['name']
        elif (isinstance(ex_name, web3.main.Web3)):
            check_dex = await search_dex(ex_name, ex_test_mode)
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

    logger.info(msg=f"Setting up {exchangeid}")
    check_cex = await search_cex(exchangeid,mode)
    check_dex = await search_dex(exchangeid,mode)
    if (check_cex):
        ex_new=check_cex
        exchange = getattr(ccxt, exchangeid)({'enableRateLimit': True,})
        exchanges[exchangeid] = exchange()
        try:
            exchanges[exchangeid] = exchange({'apiKey': ex_new[0]['api'],'secret': ex_new[0]['secret']})
            m_ordertype=ex_new[0]['ordertype']
            ex=exchanges[exchangeid]
            tickers = ex.fetch_tickers()
            for symbol, ticker in tickers.items():
               print(symbol,ticker['datetime'],'high: ' + str(ticker['high']))
               name=ex
               if (mode=="True"):
                ex.set_sandbox_mode('enabled')
                markets=ex.loadMarkets()
                return ex
            else:
                markets=ex.loadMarkets ()
                return ex
        except Exception as e:
            await handle_exception(e)
    elif (check_dex):
        ex_new= check_dex
        name= ex_new[0]['name']
        walletaddress= ex_new[0]['walletaddress']
        privatekey= ex_new[0]['privatekey']
        version= ex_new[0]['version']
        networkprovider= ex_new[0]['networkprovider']
        router= ex_new[0]['router']
        mode=ex_new[0]['testmode']
        tokenlist=ex_new[0]['tokenlist']
        abiurl=ex_new[0]['abiurl']
        abiurltoken=ex_new[0]['abiurltoken']
        basesymbol=ex_new[0]['basesymbol']
        gasLimit=ex_new[0]['gasLimit']
        gasPrice=ex_new[0]['gasPrice']
        platform=ex_new[0]['platform']
        chainId=ex_new[0]['chainId']
        ex = Web3(Web3.HTTPProvider('https://'+networkprovider))
        #ns = ns.fromWeb3(web3)
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
        logger.warning(msg=f"Error with the DB to setup {exchangeid} {ex_test_mode}, going with default")
        networkprovider='ethereum.publicnode.com'
        ex = Web3(Web3.HTTPProvider('https://'+networkprovider))
        name='uniswap'

async def search_tokenlist(parsedJson, name):
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


###DEX##SPECIFCI
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

# async def ens_resolve_dex(address):
#     try:
#         name = ns.name(address)
#         forward = ns.address(name)
#         if forward is None:
#             return None
#         if address.lower().strip() != forward.lower().strip():
#             return None
#         return name
#     except:
#         return None

async def transaction_scan_request_dex(self, address):
    url = abiurl
    query = {'module':'account',
        'action':'tokenbalance',
            'contractaddress':self.rpl_address,
            'address':address,
            'tag':'latest',
            'apikey':ethscan_api_key}
    r = requests.get(url, params=query)
    try:
        d = json.loads(r.text)
    except:
        return None
    value = int(d['result']) / self.zeroes
    return(value)

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
    current_gas_price_dex=int(ex.to_wei(ex.eth.gas_price,'wei'))
    logger.info(msg=f"current_gas_price_dex {current_gas_price_dex}")
    config_gas_price_dex=int(ex.to_wei(gasPrice,'gwei'))
    logger.info(msg=f"config_gas_price_dex {config_gas_price_dex}")
    if (current_gas_price_dex>=config_gas_price_dex):
        logger.warning(msg=f"{current_gas_price_dex} {config_gas_price_dex} ")
    else:
        logger.info(msg=f"gas setup{config_gas_price_dex} aligned with current gas price {current_gas_price_dex}")
    # checkgasLimitURL = abiurl + "?module=stats&action=dailyavggaslimit&startdate=2022-01-09&enddate=2022-01-09&sort=asc&apikey=" + abiurltoken
    # checkgasLimitRequest = requests.get(url=checkgasLimitURL,headers=headers)
    # gasLimitresults = checkgasLimitRequest.json()['result']['gasLimit']
    # logger.info(msg=f"gasLimitresults {gasLimitresults}")
    # if (gasLimit<=gasLimitresults):
    #     logger.warning(msg=f"gaslimit warning: {gasLimit} {gasLimitresults}")

async def fetch_token_price(s1):
# try:
#     coininfo=ex_gecko_api.search(query=s1)
#     for i in coininfo['coins']:
#         fetch_tokeninfo=i['symbol']
#         if (fetch_tokeninfo == s1):
#             # logger.info(msg=f"{i['api_symbol']}")
#             coininfo=ex_gecko_api.get_coin_by_id(id=i['api_symbol'])
#             coinplatform=coininfo['asset_platform_id']
#             # logger.info(msg=f"coinplatform {coinplatfrom}")
#             coinprice=coininfo['market_data']['current_price']['usd']
#             # logger.info(msg=f"coingeckoprice {coinprice}")
#             coinsymbol=coininfo['symbol']
#             response = f'coingecko info: {coinsymbol} {coinprice} USD on {coinplatform}'
#             logger.info(msg=f"{response}")
#             return coinprice
# except Exception:
#     return
    try:
        # Search for WBTC on CoinGecko
        coin_info = ex_gecko_api.get_coin_by_id(id=s1)
        # Get the WBTC token's contract address on the chain
        for token in coin_info['contract']:
            if token['chain_id'] == str(chain_id):
                token_address = token['contract_address']
                print(f"address: {token_address}")
                return token_address
    except Exception as e:
        print(f"An error occurred while retrieving address {e}")


async def verify_latency_ex():
    try:
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
            response = round(ping(networkprovider, unit='ms'),3)
            return response
    except Exception as e:
        await handle_exception(e)


async def sign_transaction_dex(contract_tx):
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
            asset_out_symbol=basesymbol
            asset_in_symbol=s2
        else:
            asset_out_symbol=s2
            asset_in_symbol=basesymbol
        asset_out_address=ex.to_checksum_address(await search_contract_dex(asset_out_symbol))
        asset_out_abi= await fetch_abi_dex(asset_out_address)
        asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
        asset_in_address= ex.to_checksum_address(await search_contract_dex(asset_in_symbol))
        order_path_dex=[asset_out_address, asset_in_address]
        asset_out_balance=asset_out_contract.functions.balanceOf(walletaddress).call()
        if (asset_out_balance <=0):
            return
        logger.info(msg=f"asset_out_balance {asset_out_balance}")
        asset_out_decimals=asset_out_contract.functions.decimals().call()
        slippage=1
        if (s1=="SELL"):
            asset_out_amount = (asset_out_balance)/(10 ** asset_out_decimals) #SELL all token in case of sell order
            response = f"⬇️ {s2}"
            asset_out_quote= await fetch_token_price(asset_out_symbol)
        else:
            asset_out_amount = ((asset_out_balance)/(10 ** asset_out_decimals))*(float(s5)/100) #buy %p ercentage
            response = f"⬆️ {s2}"
        asset_in_quote= await fetch_token_price(asset_in_symbol)
        asset_out_amount_converted = (ex.to_wei(asset_out_amount,'ether'))
        transaction_amount = asset_out_amount_converted
        # deadline = ex.eth.getBlock("latest")["timestamp"] + 3600
        deadline = (int(time.time()) + 1000000)
        if (version=='v2'):
            approvalcheck = asset_out_contract.functions.allowance(ex.to_checksum_address(walletaddress), ex.to_checksum_address(router)).call()
            logger.info(msg=f"approvalcheck {approvalcheck}")
            if (approvalcheck==0):
                approved_amount = (ex.to_wei(2**64-1,'ether'))
                approval_TX = asset_out_contract.functions.approve(ex.to_checksum_address(router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                logger.info(msg=f"Approval {str(ex.to_hex(approval_txHash))}")
                time.sleep(10) #wait approval
                transaction_getoutput_amount  = router_instance.functions.getOutputAmount(transaction_amount, order_path_dex).call()
            transaction_minimum_amount = int(transaction_getoutput_amount[1] *0.98)# max 2% slippage
            swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_minimum_amount,order_path_dex,walletaddress)
            tx_token = await sign_transaction_dex(swap_TX)
        elif (version=="1inch"):
            logger.info(msg=f"1inch processing")
            logger.info(msg=f"{transaction_amount}")
            approval_URL = f"{dex_1inch_api}/{chainId}/approve/transaction?tokenAddress={tokenToSell}"
            logger.info(msg=f"{approval_URL}")
            approval_response = requests.get(approval_URL)
            approval= approval_response.json()
            logger.info(msg=f"approval {approval}")
            swap_url = f"{dex_1inch_api}/{chainId}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={walletaddress}&slippage={slippage}"
            logger.info(msg=f"swap_url {swap_url}")
            swap_response = requests.get(swap_url)
            logger.info(msg=f"swap_response {swap_response}")
            swap_raw = swap_response.json()
            logger.info(msg=f"swap_raw {swap_raw}")
            # tx_token = await sign_transaction_dex(swap_raw)
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
            # #OptimalOrderAmount  = quoter_instance.functions.getSwapQuote(tokenToSell, transaction_amount, tokenToBuy).call()
            # #MinimumAmount=int(OptimalOrderAmount[1] *0.98)# max 2% slippage
            # swap_TX=router_instance.functions.addOrder(tokenToBuy,transaction_amount,tokenToSell,OrderAmountfee)
            # tx_token = await sign_transaction_dex(swap_TX)
        elif (version =="limitorder"):
            logger.info(msg=f"limitorder processing")
            return
        else:
            return
        txHash = str(ex.to_hex(tx_token))
        checkTransactionSuccessURL = abiurl + "?module=transaction&action=gettxreceiptstatus&txhash=" + txHash + "&apikey=" + abiurltoken
        checkTransactionRequest = requests.get(url=checkTransactionSuccessURL,headers=headers)
        txResult = checkTransactionRequest.json()['status']
        #await verify_gas_dex()
        txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
        coinprice=fetch_token_price()
        gasUsed=txHashDetail['gasUsed']
        txtimestamp=datetime.now()
        if(txResult == "1"):
            response+= f"\n➕ Size: {round(ex.from_wei(transaction_amount, 'ether'),5)}\n⚫️ Entry: {coinprice}USD \nℹ️ {txHash}\n⛽️ {gasUsed}\n🗓️ {txtimestamp}"
            logger.info(msg=f"{response}")
            return response
    except Exception as e:
        await handle_exception(e)
        return

async def fetch_tokeninfo(token):
    global token_price
    global asset_info
    #asset_platforms = cg.get_asset_platforms()
    #logger.info(msg=f"cg.get_asset_platforms {asset_platforms}")
    try:
        #coininfo=cg.get_coin_by_id(id=token)
        #coinplatform=coininfo['asset_platform_id']
        #coindescription=coininfo['description']['en']
        #  coinprice=coininfo['market_data']['current_price']['usd']
        # coinsymbol=coininfo['symbol']
        #coinlink='https://www.coingecko.com/en/coins/'+coininfo['symbol']
        # response = f'{coinsymbol} {coinprice} USD \n{coindescription}\n{coinlink}'
        #logger.info(msg=f"{response}")
        #  return response
        coininfo=ex_gecko_api.search(query=symbol)
        for i in coininfo['coins']:
            results_search_coin = i['symbol']
            if (results_search_coin==symbol):
                logger.info(msg=f"Pass")
                logger.info(msg=f"{i['api_symbol']}")
                coininfo=ex_gecko_api.get_coin_by_id(id=i['api_symbol'])
                coinplatform=coininfo['asset_platform_id']
                logger.info(msg=f"coinplatfrom {coinplatfrom}")
                coinprice=coininfo['market_data']['current_price']['usd']
                logger.info(msg=f"coinprice {coinprice}")
                coinsymbol=coininfo['symbol']
                response = f'{coinsymbol} {coinprice} USD on {coinplatform}'
                logger.info(msg=f"{response}")
    except Exception:
        return

async def fetch_tokeninfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    parsed_symbol=parsed_message[1].upper()
    try:
        await fetch_tokeninfo(parsed_symbol)
    except Exception as e:
        return


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
    if (bot_token is not None):
        apobj.add('tgram://' + str(bot_token) + "/" + str(bot_channel_id))
        try:
            apobj.notify(body=messaging)
        except Exception as e:
            logger.error(msg=f"error: {e}")
        else:
            logger.error(msg=f"not delivered {messaging}")
#======= error handling
async def handle_exception(e) -> None:
    try:
        msg = f"error:"
        logger.error(msg=f"error: {e}")
    except KeyError:
        msg = f"DB content error"
        sys.exit()
    except IndexError:
        msg = f"Parsing error"
    except telegram.error:
        msg = f"telegram error"
    except ConnectionError:
        msg = f'Could not connect to RPC'
    except Web3Exception.error:
        msg = f"web3 error"
    except ccxt.base.errors:
        msg = f"CCXT error"
    except ccxt.NetworkError:
        msg = f"Network error"
    except ccxt.ExchangeError:
        msg = f"Exchange error"
    except Exception:
        msg = f"{e}"
        message = f"⚠️ {msg} {e}"
        logger.error(msg = f"{message}")
        await notify(message)
##======== END OF FUNCTIONS ============

##============TG COMMAND================
##====view help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r_ping = await verify_latency_ex()
    msg= f"Environment: {env} Ping: {r_ping}ms\nExchange: {await search_exchange(ex,ex_test_mode)} Sandbox: {ex_test_mode}\n{bot_menu_help}"
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
            sbal = ""
            for iterator in bal:
                sbal += (f"{iterator}: {bal[iterator]} \n")
                if(sbal == ""):
                    sbal = "No Balance"
                    msg += f"\n{sbal}"
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
    msg = ""
    if [ele for ele in filter_lst if(ele in uppercased_message)]:
        if (bot_trading_switch == False):
            message = "TRADING DISABLED"
            await send(update,message)
        else:
            try:
                order_m = convert(uppercased_message)
                m_dir = order_m[0]
                m_symbol = order_m[1]
                m_sl = order_m[2]
                m_tp = order_m[3]
                m_q = order_m[4]
                logger.info(msg = f"Processing order: {m_dir} {m_symbol} {m_sl} {m_tp} {m_q}")
                res = await send_order(m_dir,m_symbol,m_sl,m_tp,m_q)
                if (res != None):
                    response = f"{res}"
                    await send(update,response)
            except Exception as e:
                await handle_exception(e)
                return
##======TG COMMAND view price ===========
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    if [ele for ele in filter_quote if(ele in parsed_message)]:
        symbol=parsed_message[1]
        try:
            if not (isinstance(ex,web3.main.Web3)):
                price= ex.fetch_ticker(symbol.upper())['last']
                response=f"₿ {symbol} @ {price}"
            elif (isinstance(ex,web3.main.Web3)):
                if(await search_contract_dex(symbol) != None):
                    asset_in_address = ex.to_checksum_address(await search_contract_dex(symbol))
                    asset_out_address =ex.to_checksum_address(await search_contract_dex('USDT'))
                    if(symbol_to_quote != None):
                        fetch_tokeninfo=ex_gecko_api.get_coin_info_from_contract_address_by_id(id=platform,contract_address=symbol_to_quote)
                        asset_out_cg_quote=fetch_tokeninfo['market_data']['current_price']['usd']
                        asset_out_amount=1
                        quote_url = f"{dex_1inch_api}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
                        quote_response = requests.get(quote_url)
                        quote = quote_response.json()
                        asset_out_quote = quote['toTokenAmount']
                        response=f"₿ {symbol_to_quote}\n{symbol} @ {asset_out_quote} (1inch - live) or {asset_out_cg_quote} (gecko)"
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
    token=parsed_message[1]
    try:
        response=await fetch_tokeninfo(token)
        await send(update,response)
    except Exception as e:
        await handle_exception(e)
        return

##====TG COMMAND Trading switch  ========
async def trading_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_trading_switch
    if (bot_trading_switch==False):
        bot_trading_switch=True
    else:
        bot_trading_switch=False
        message=f"Trading is {bot_trading_switch}"
        await send(update,message)

##====TG COMMAND CEX DEX switch =========
async def switch_exchange_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_message  = update.effective_message.text
    parsed_message = channel_message.split(" ")
    ex_new =parsed_message[1]
    ex_type=parsed_message[0]
    try:
        if (ex_type == "/cex"):
            results_search_cex = await search_cex(ex_new,ex_test_mode)
            CEX_name = results_search_cex[0]['name']
            res = await load_exchange(CEX_name,ex_test_mode)
            response = f"CEX is {ex}"
        elif (ex_type == "/dex"):
            results_search_dex = await search_dex(ex_new,ex_test_mode)
            DEX_name= results_search_dex[0]['name']
            res = await load_exchange(DEX_name,ex_test_mode)
            response = f"DEX is {DEX_name}"
            await send(update,response)
    except Exception as e:
        await handle_exception(e)
##======TG COMMAND Test mode switch ======
async def switch_testmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ex_test_mode
    if (ex_test_mode == "False"):
        ex_test_mode = "True"
    else:
        ex_test_mode = "False"
        message = f"Test mode is {ex_test_mode}"
        await send(update, message)

##======== DB START ===============
db_url=os.getenv("DB_URL")
if db_url == None:
    logger.info(msg = f"No remote DB")
else:
    outfile = os.path.join('./config', 'db.json')
    response = requests.get(db_url, stream=True)
    logger.info(msg=f"{response}")
    with open(outfile,'wb') as output:
      output.write(response.content)
      logger.info(msg = f"copied the remote DB")

db_path = './config/db.json'
if os.path.exists(db_path):
    logger.info(msg=f"Existing DB")
    try:
        db = TinyDB(db_path)
        q = Query()
        globalDB = db.table('global')
        env = globalDB.all()[0]['env']
        ex = globalDB.all()[0]['defaultex']
        ex_test_mode = globalDB.all()[0]['defaulttestmode']
        logger.info(msg=f"Env {env} ex {ex}")
        bot_db = db.table('telegram')
        cex_db = db.table('cex')
        dex_db = db.table('dex')
        tg = bot_db.search(q.platform == env)
        bot_token = tg[0]['token']
        bot_channel_id = tg[0]['channel']
        bot_webhook_port = tg[0]['port']
        bot_webhook_secret = tg[0]['secret_token']
        bot_webhook_privatekey = tg[0]['key']
        bot_webhook_certificate = tg[0]['cert']
        bot_webhook_url = tg[0]['webhook_url']
        if (bot_token == ""):
            logger.error("no TG TK")
            logger.info(msg=f"Failover process with sample DB")
            contingency_db_path = './config/sample_db.json'
            os.rename(contingency_db_path, db_path)
            try:
                bot_token = os.getenv("TG_TK")
                bot_channel_id = os.getenv("TG_CHANNEL_ID")
            except Exception as e:
                logger.error("no telegram token")
                sys.exit()
    except Exception:
        logger.warning(msg=f"error with existing db file {db_path}")

##========== startup message ===========
async def post_init(application: Application):
    message=f"Bot is online {TTversion}"
    await load_exchange(ex,ex_test_mode)
    logger.info(msg=f"{message}")
    await application.bot.send_message(bot_channel_id, message, parse_mode=constants.ParseMode.HTML)

#===========bot error handling ==========
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e = f"{tb_trim}"
    await handle_exception(e)

#================== BOT =================
def main():
    try:
        verify_import_library()
#Starting Bot TPB
        application = Application.builder().token(bot_token).post_init(post_init).build()

#TPBMenusHandlers
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), bal_command))
        application.add_handler(MessageHandler(filters.Regex('/q'), quote_command))
        application.add_handler(MessageHandler(filters.Regex('/c'), coininfo_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), trading_switch_command))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), monitor))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), switch_exchange_command))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), switch_testmode_command))
        application.add_handler(MessageHandler(filters.Regex('/g'), fetch_tokeninfo_command))
        application.add_handler(MessageHandler(filters.Regex('/restart'), restart_command))
        application.add_error_handler(error_handler)
        # application.add_handler(MessageHandler(filters.Regex('/dbdisplay'), showDB_command))
        # application.add_handler(MessageHandler(filters.Regex('/dbpurge'), dropDB_command))

    #Run the bot
        webhook = False
        if (webhook):
            logger.info(f"Webhook start")
            try:
                application.run_webhook(
                    listen='0.0.0.0',
                    port=bot_webhook_port,
                    webhook_url=bot_webhook_url)
            except Exception as e:
                logger.error("Bot failed to start. Error: " + str(e))
        else:
            try:
                application.run_polling(drop_pending_updates=True)
            except telegram.error.Conflict:
                logger.error(msg='Bot failed to start due to conflict')
                sys.exit()

    except Exception as e:
        logger.info(msg="Bot failed to start. Error: " + str(e))


if __name__ == '__main__':
    main()
