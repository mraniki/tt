##=============== VERSION =============
TTversion="🪙TT Beta 1.03.23"
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
from tinydb import TinyDB, Query, where
import re
#CEX
import ccxt
#DEX
import web3
from web3 import Web3
from web3.contract import Contract
#from pywalletconnect.client import WCClient
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
ex_name = "pancake"
chainId = 56
exchanges = {}
bot_trading_switch=True
ex_test_mode = "True"
#=======API endpoint
headers = { "User-Agent": "Mozilla/5.0" }
gecko_api = CoinGeckoAPI()

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
        bot_db.insert({"token": s1, "channel": s2, "env": s3})

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


###MESSAGEPARSER
async def parse_message (message):
    wordlist = message.split(" ")
    logger.info(msg=f"{wordlist}")
    filter_lst_order = ['BUY', 'SELL', 'buy','sell']
    filter_lst_switch = ['/cex', '/dex']
    filter_lst_quote = ['/q','/c']
    logger.info(msg=f"{len(wordlist)}")
    try:
        if [ele for ele in filter_lst_order if(ele in wordlist)]:
            if len(wordlist[0]) > 0:
                direction = wordlist[0]
                if len(wordlist[1]) > 0:
                    symbol = wordlist[1]
                    m_sl=0
                    m_tp=0
                    m_q=5
                    order=[direction,symbol,m_sl,m_tp,m_q]
                    logger.info(msg=f"{symbol}")
                    return order
        elif [ele for ele in filter_lst_switch if(ele in wordlist)]:
            if len(wordlist[1]) > 0:
                return wordlist[1]
            else:
                return
        elif [ele for ele in filter_lst_quote if(ele in wordlist)]:
            if len(wordlist[1]) > 0:
                return wordlist[1]
            else:
                return
        else:
            return
    except Exception as e:
        await handle_exception(e)
        logger.warning(msg=f"Message parsing anomaly")
        return

#=========Exchange Functions

async def search_exchange(searched_data):
    results_cex = cex_db.search((where('name')==searched_data) & (where ('testmode') == ex_test_mode))
    results_dex = dex_db.search((where('name')==searched_data) & (where ('testmode') == ex_test_mode))
    if (len(results_cex) >= 1):
        for result in results_cex:
            return result
    elif (len(results_dex) >= 1):
        for result in results_dex:
            return result
    else:  
        return None

async def load_exchange(exchangeid):
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
    global quoter_instance
    global quoter_instanceabi
    global env
    global chainId
    global ex_test_mode
    global platform

    logger.info(msg=f"Setting up {exchangeid}")
    check_ex = await search_exchange(exchangeid)
    if ('walletaddress' in check_ex):
        ex_new= check_ex
        name= ex_new['name']
        walletaddress= ex_new['walletaddress']
        privatekey= ex_new['privatekey']
        version= ex_new['version']
        networkprovider= ex_new['networkprovider']
        router= ex_new['router']
        ex_test_mode=ex_new['testmode']
        tokenlist=ex_new['tokenlist']
        abiurl=ex_new['abiurl']
        abiurltoken=ex_new['abiurltoken']
        basesymbol=ex_new['basesymbol']
        gasLimit=ex_new['gasLimit']
        gasPrice=ex_new['gasPrice']
        platform=ex_new['platform']
        chainId=ex_new['chainId']
        logger.info(msg=f"chainId {chainId}")
        ex = Web3(Web3.HTTPProvider('https://'+networkprovider))
        #ns = ns.fromWeb3(web3)
        router_instanceabi= await fetch_abi_dex(router) #Router ABI
        router_instance = ex.eth.contract(address=ex.to_checksum_address(router), abi=router_instanceabi) #ContractLiquidityRouter
        if (version=="v3"):
            quoter_instanceabi= await fetch_abi_dex(quoter_instance) #Quoter ABI
            quoter_instance = ex.eth.contract(address=ex.to_checksum_address(quoter_instanceabi), abi=quoter_instanceabi) #ContractLiquidityQuoter
        try:
            ex.net.listening
            logger.info(msg=f"connected to {ex}")
            return name
        except Exception as e:
            await handle_exception(e)
    elif ('api' in check_ex):
        exchange_id = check_ex['name']
        client = getattr(ccxt, exchange_id)
        try:
            exchange = client({'apiKey': check_ex['api'],'secret': check_ex['secret']})
            m_ordertype=check_ex['ordertype']
            ex=exchange
            if (ex_test_mode=="True"):
                ex.set_sandbox_mode('enabled')
            markets= ex.loadMarkets()
            return ex
        except Exception as e:
            await handle_exception(e)
    else:
        return

#========== Order function

async def execute_order(s1,s2,s3,s4,s5):
    try:
        if not isinstance(ex,web3.main.Web3):
            logger.info(msg=f"cex order: {s1} {s2} {s3} {s4} {s5}")
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            if (len(str(bal))):
                m_price = float(ex.fetchTicker(f'{s2}').get('last'))
                totalusdtbal = ex.fetchBalance()['USDT']['free']
            amountpercent=((totalusdtbal)*(float(s5)/100))/float(m_price) # % of bal
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

        elif (isinstance(ex,web3.main.Web3)):
            response = await send_order_dex(s1,s2,s3,s4,s5)
        else:
            response('review order')
        return response
    except Exception as e:
        await handle_exception(e)
        return


async def send_order_dex(s1,s2,s3,s4,s5):
    dex_1inch_api = f"https://api.1inch.exchange/v5.0/{chainId}"
    try:
        if (s1=="BUY"):
            asset_out_symbol=basesymbol
            asset_in_symbol=s2
        else:
            asset_out_symbol=s2
            asset_in_symbol=basesymbol
        asset_out_address=ex.to_checksum_address(await search_gecko_contract(asset_out_symbol))
        asset_out_abi= await fetch_abi_dex(asset_out_address)
        asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
        asset_in_address= ex.to_checksum_address(await search_gecko_contract(asset_in_symbol))
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
        deadline = ex.eth.get_block("latest")["timestamp"] + 3600
        #deadline = (int(time.time()) + 1000000)
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
        #transaction_scanner(txHash)
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


##DEX specific

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
        if(abi!=""):
            return abi
        else:
            return None
    except Exception as e:
        await handle_exception(e)

# async def search_tokenlist(parsedJson, token):
#     for entry in parsedJson:
#         if token == entry ['symbol']:
#             if int(chainId) == entry ['chainId']:
#                 return entry ['address']

# async def search_contract_dex(symb):
#     try:
#         url = requests.get(tokenlist)
#         text = url.text
#         token_list = json.loads(text)['tokens']
#         try:
#             symbolcontract= await search_tokenlist(token_list,symb)
#             if symbolcontract != None:
#                 return symbolcontract
#             else:
#                 msg=f"{symb} does not exist in {tokenlist}"
#                 await handle_exception(msg)
#                 return
#         except Exception as e:
#             return
#     except Exception as e:
#         return

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

# async def transaction_scanner (address):
#     url = abiurl
#     query = {'module':'account',
#             'action':'tokenbalance',
#             'contractaddress':self.rpl_address,
#             'address':address,
#             'tag':'latest',
#             'apikey':ethscan_api_key}
#     r = requests.get(url, params=query)
#     try:
#         d = json.loads(r.text)
#     except:
#         return None
#     value = int(d['result']) / self.zeroes
#     return(value)

async def verify_gas_dex():
    current_gas_price_dex=int(ex.to_wei(ex.eth.gas_price,'wei'))
    config_gas_price_dex=int(ex.to_wei(gasPrice,'gwei'))
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

#===========GECKO
async def search_gecko(token):
    try:
        symbol_info = gecko_api.search(query=token)
        #logger.info(msg=f"symbol_info {symbol_info}")
        for i in symbol_info['coins']:
            results_search_coin = i['symbol']
            if (results_search_coin==token.upper()):
                api_symbol = i['api_symbol']
                #logger.info(msg=f"api info {api_symbol}")
                return api_symbol
    except Exception:
        return

async def search_gecko_detailed(token):
    try:
        coin_info = gecko_api.get_coin_by_id(id=f'{await search_gecko(token)}')
        await search_gecko_platform()
        await search_gecko_contract(token)
        #logger.info(msg=f"coininfo {coininfo}")
        coin_symbol= coin_info['symbol']
        coin_platform = coin_info['asset_platform_id']
        response = f'Symbol {coin_symbol}\nPlatform {coin_platform}'
        return response
    except Exception:
        return

async def search_gecko_platform():
    try:
        assetplatform = gecko_api.get_asset_platforms()
        for i in assetplatform:
            results_search_chain = i['chain_identifier']
            if (results_search_chain == int(chainId)):
                response = i['id']
                return response
    except Exception:
        return

async def search_gecko_contract(token):
    try:
        coin_info = gecko_api.get_coin_by_id(id=f'{await search_gecko(token)}')
        coin_contract = coin_info['platforms'][f'{await search_gecko_platform()}']
        logger.info(msg=f"search gecko contract {token} {coin_contract}")
        return coin_contract
    except Exception:
        return

async def fetch_token_price(token):
    try:
        coin_info = gecko_api.get_coin_by_id(id=f'{await search_gecko(token)}')
        for token in coin_info['contract']:
            if token['chain_id'] == str(chain_id):
                token_address = token['contract_address']
                print(f"address: {token_address}")
                return token_address
    except Exception as e:
        print(f"An error occurred while retrieving address {e}")

async def search_gecko_exchange(exchange):
    try:
        exchange_list = gecko_api.get_exchanges_list()
        for i in exchange_list:
            results_search_exchange = i['id']
            if (results_search_exchange == exchange):
                response = i
                return response
    except Exception:
        return

#===========QUOTE
async def fetch_gecko_quote(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=platform,contract_address=asset_in_address)
        #logger.info(msg=f"fetch_tokeninfo{fetch_tokeninfo}")
        asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
        asset_out_cg_name = fetch_tokeninfo['name']
        response = f"{asset_out_cg_name}\n🦎{asset_out_cg_quote} USD\n🖊️{chainId}: {asset_in_address}"
        return response
    except Exception:
        return

async def fetch_1inch_quote(token):
    dex_1inch_api = f"https://api.1inch.exchange/v5.0/{chainId}"
    asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
    asset_out_address =ex.to_checksum_address(await search_gecko_contract('USDC'))
    try:
        asset_out_amount=100000
        quote_url = f"{dex_1inch_api}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
        logger.debug(msg=f"quote_url{quote_url}")
        quote_response = requests.get(quote_url)
        logger.debug(msg=f"quote_response{quote_response}")
        quote = quote_response.json()
        asset_out_1inch_quote = quote['toTokenAmount']
        return asset_out_1inch_quote
    except Exception:
        return

async def fetch_dex_quote(token):
    try:
        return
    except Exception:
        return


####UTILS
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

async def convert_currency(_from_: 'USD', _to_: 'EUR',amount):
    ex_ccyrate_api = f"https://api.exchangerate.host"
    try:
        url = f"{ex_ccyrate_api}/convert?from={_from_}&to={_to_}&amount={amount}"
        response = requests.get(url)
        rate = response.json()
        return rate["result"]
    except Exception as e:
        await handle_exception(e)
        logger.warning(msg=f"API conversion error {e}")
        return

#=========== PRIVATE

async def get_account_balance():
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
        elif (isinstance(ex,web3.main.Web3)):
            bal = ex.eth.get_balance(walletaddress)
            bal = round(ex.from_wei(bal,'ether'),5)
            msg += f"\n{bal}"
        else:
            msg += "0"
        return msg
    except Exception as e:
        return

async def get_account_position():
    try:
        return
    except Exception as e:
        return

async def get_wallet_auth():
    try:
        return
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

##============BOT COMMAND================
##====view help =====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r_ping = await verify_latency_ex()
    msg= f"Environment: {env} Ping: {r_ping}ms\nExchange: {await search_exchange(ex_name)} Sandbox: {ex_test_mode}\n{bot_menu_help}"
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
    balance = await get_account_balance()
    await send(update,balance)
#===orderscanner======
async def order_scanner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message = update.effective_message.text
    order = await parse_message(channel_message)
    if (order):
        if (bot_trading_switch == False):
            message = "TRADING DISABLED"
            await send(update,message)
        else:
            try:
                direction = order[0]
                symbol = order[1]
                stoploss = order[2]
                takeprofit = order[3]
                quantity = order[4]
                logger.info(msg = f"Processing order: {direction} {symbol} {stoploss} {takeprofit} {quantity}")
                res = await execute_order(direction,symbol,stoploss,takeprofit,quantity)
                if (res != None):
                    response = f"{res}"
                    await send(update,response)
            except Exception as e:
                await handle_exception(e)
                return
##====== view quote ===========
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message = update.effective_message.text
    symbol = await parse_message(channel_message)
    logger.info(msg=f"searching for  {symbol}")
    asset_out_cg_quote = await fetch_gecko_quote(symbol)
    response=f"₿ {asset_out_cg_quote}\n"
    try:
        if (isinstance(ex,web3.main.Web3)):
            if(await search_gecko_contract(symbol) != None):
                asset_out_1inch_quote = await fetch_1inch_quote (symbol)
                response+=f"🦄 {asset_out_1inch_quote} USD"
                await send(update,response)
        elif not (isinstance(ex,web3.main.Web3)):
            price= ex.fetch_ticker(symbol.upper())['last']
            response+=f"🏛️ {price} USD"
    except Exception as e:
        await handle_exception(e)
        return

##====== view tokeninfo ===========
async def get_tokeninfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol= await parse_message(update.effective_message.text)
    gecko_symbol_info = await search_gecko_detailed(symbol)
    await send(update,gecko_symbol_info)

##==== COMMAND Trading switch  ========
async def trading_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_trading_switch
    if (bot_trading_switch==False):
        bot_trading_switch=True
    else:
        bot_trading_switch=False
        message=f"Trading is {bot_trading_switch}"
        await send(update,message)

##==== COMMAND CEX DEX switch =========
async def exchange_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_exchange  = parse_message(update.effective_message.text)
    results = await search_exchange(new_exchange)
    ex_name = results['name']
    res = await load_exchange(ex_name)
    response = f"{ex_name} is active"
    await send(update,response)

##====== COMMAND Test mode switch ======
async def testmode_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        defaultenv = globalDB.all()[0]['defaultenv']
        ex_name = globalDB.all()[0]['defaultex']
        ex_test_mode = globalDB.all()[0]['defaulttestmode']
        logger.info(msg=f"Env {defaultenv} ex {ex_name}")
        bot_db = db.table('bot')
        cex_db = db.table('cex')
        dex_db = db.table('dex')
        bot = bot_db.search(q.env == defaultenv)
        logger.info(msg=f"{bot}")
        bot_token = bot[0]['token']
        bot_channel_id = bot[0]['channel']
        bot_webhook_port = bot[0]['port']
        bot_webhook_secret = bot[0]['secret_token']
        bot_webhook_privatekey = bot[0]['key']
        bot_webhook_certificate = bot[0]['cert']
        bot_webhook_url = bot[0]['webhook_url']
        if (bot_token == ""):
            logger.error("no TG TK")
            logger.info(msg=f"Failover process with sample DB")
            contingency_db_path = './config/sample_db.json'
            os.rename(contingency_db_path, db_path)
            try:
                bot_token = os.getenv("TG_TK")
                bot_channel_id = os.getenv("TG_CHANNEL_ID")
            except Exception as e:
                logger.error("no bot token")
                sys.exit()
    except Exception as e:
        logger.warning(msg=f"error with db file {db_path}, Verify Json. error: {e}")

##========== startup message ===========
async def post_init(application: Application):
    message=f"Bot is online {TTversion}"
    await load_exchange(ex_name)
    logger.warning(msg=f"exchange type {type(ex)}")
    logger.warning(msg=f"exchange isinstance {isinstance(ex,web3.main.Web3)}")
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
        application.add_handler(MessageHandler(filters.Regex('/c'), get_tokeninfo_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), trading_switch_command))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), order_scanner))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), exchange_switch_command))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), testmode_switch_command))
        application.add_handler(MessageHandler(filters.Regex('/t'), search_gecko))
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
