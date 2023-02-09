##=============== VERSION =============
TTversion="🪙TT Beta 1.2.30"
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
from ens import ENS 
from web3.middleware import geth_poa_middleware
#from pywalletconnect.client import WCClient
from typing import List
import time
from datetime import datetime
from pycoingecko import CoinGeckoAPI

#🔧CONFIG
load_dotenv()

#🧐LOGGING
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

#🔗API
gecko_api = CoinGeckoAPI()
dex_1inch_api = f"https://api.1inch.exchange/v5.0"
exchangerate_api = f"https://api.exchangerate.host"

#🔁UTILS
def verify_import_library():
    logger.info(msg=f"{TTversion}")
    logger.debug(msg=f"Python {sys.version}")
    logger.debug(msg=f"TinyDB {tinydb.__version__}")
    logger.debug(msg=f"TPB {telegram.__version__}")
    logger.debug(msg=f"CCXT {ccxt.__version__}")
    logger.debug(msg=f"Web3 {web3.__version__}")
    logger.debug(msg=f"apprise {apprise.__version__}")

async def parse_message (message):
    wordlist = message.split(" ")
    logger.debug(msg=f"wordlist {wordlist}")
    filter_lst_order = ['BUY', 'SELL', 'buy','sell']
    filter_lst_switch = ['/cex', '/dex']
    filter_lst_quote = ['/q','/coin']
    logger.debug(msg=f"wordlist len {len(wordlist)}")
    try:
        if [ele for ele in filter_lst_order if(ele in wordlist)]:
            if len(wordlist[0]) > 0:
                direction = wordlist[0].upper()
                if len(wordlist[1]) > 0:
                    symbol = wordlist[1]
                    stoploss = 100
                    takeprofit = 100
                    quantity = 10
                    if len(wordlist[2]) > 0:
                        stoploss = wordlist[2][3:]
                        takeprofit = wordlist[3][3:]
                        quantity = wordlist[4][2:-1]
                    order=[direction,symbol,stoploss,takeprofit,quantity]
                    logger.debug(msg=f"Order: {order}")
                    return order
        elif [ele for ele in filter_lst_switch if(ele in wordlist)]:
            if len(wordlist[1]) > 0:
                exchange = wordlist[1]
                logger.debug(msg=f"filter_lst_switch {wordlist[1]} {exchange}")
                exchange_search = await search_exchange(exchange)
                return exchange_search
            else:
                return
        elif [ele for ele in filter_lst_quote if(ele in wordlist)]:
            if len(wordlist[1]) > 0:
                symbol = wordlist[1]
                logger.info(msg=f"filter_lst_quote {wordlist[1]} {symbol}")
                return symbol
            else:
                return
        else:
            return
    except Exception as e:
        await handle_exception(e)
        logger.warning(msg=f"Message parsing anomaly")
        return

async def retrieve_url_json(url,params=None):
    headers = { "User-Agent": "Mozilla/5.0" }
    #logger.info(msg=f"url {url} {params} ")
    response = requests.get(url,params =params,headers=headers)
    #logger.info(msg=f"response {response} ")
    response_json = response.json()
    #logger.info(msg=f"response_json {response_json} ")
    return response_json

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
                results.append(elapsed)
                rtt = int(sum(results) / len(results))
                response = rtt
        elif (isinstance(ex,web3.main.Web3)):
            response = round(ping(ex_node_provider, unit='ms'),3)
            return response
    except Exception as e:
        await handle_exception(e)

async def convert_currency(_from_: 'USD', _to_: 'EUR',amount):
    try:
        url = f"{ex_ccyrate_api}/convert?from={_from_}&to={_to_}&amount={amount}"
        rate = await retrieve_url_json(url)
        return rate["result"]
    except Exception as e:
        await handle_exception(e)
        logger.warning(msg=f"API conversion error {e}")
        return

#💬MESSAGING
async def send (self, messaging):
    try:
        await self.effective_chat.send_message(f"{messaging}", parse_mode=constants.ParseMode.HTML)
    except Exception as e:
        await handle_exception(e)

async def notify(messaging):
    apobj = apprise.Apprise()
    if (bot_token is not None):
        apobj.add('tgram://' + str(bot_token) + "/" + str(bot_channel_id))
        try:
            apobj.notify(body=messaging)
        except Exception as e:
            logger.error(msg=f"delivered: {e}")
    else:
        logger.error(msg=f"not delivered {messaging}")

#💱EXCHANGE
async def search_exchange(searched_data):
    results_cex = cex_db.search((where('name')==searched_data) & (where ('testmode') == ex_test_mode))
    logger.debug(msg=f"results_cex {results_cex}")
    results_dex = dex_db.search((where('name')==searched_data) & (where ('testmode') == ex_test_mode))
    logger.debug(msg=f"results_dex {results_dex}")
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
    global ex_name
    global ex_test_mode
    global price_type
    global ex_node_provider
    global dex_version
    global walletaddress
    global privatekey
    global chainId
    global router
    global abiurl
    global abiurltoken
    global basesymbol
    global gasPrice
    global gasLimit
    global router_instance
    global router_instanceabi
    global quoter_instance
    global quoter_instanceabi
    global ns

    logger.info(msg=f"Setting up {exchangeid}")
    ex_result = await search_exchange(exchangeid)
    #logger.info(msg=f"ex_result {ex_result}")
    exchange_info = await search_gecko_exchange(exchangeid)
    #logger.info(msg=f"exchange_info {exchange_info}")
    if ('router' in ex_result):
        ex_name = ex_result['name']
        ex_test_mode=ex_result['testmode']
        ex_node_provider= ex_result['networkprovider']
        router= ex_result['router']
        abiurl=ex_result['abiurl']
        abiurltoken=ex_result['abiurltoken']
        basesymbol=ex_result['basesymbol']
        dex_version= ex_result['version']
        gasLimit=ex_result['gasLimit']
        gasPrice=ex_result['gasPrice']
        chainId=ex_result['chainId']
        walletaddress= ex_result['walletaddress']
        privatekey= ex_result['privatekey']
        ex = Web3(Web3.HTTPProvider('https://'+ex_node_provider))
        ex.middleware_onion.inject(geth_poa_middleware, layer=0)
        #ns = ENS.from_web3(ex)
        #await resolve_ens_dex(router)
        router_instanceabi= await fetch_abi_dex(router) #Router ABI
        #buy BNB sl=1000 tp=300 q=20%logger.info(msg=f"router_instanceabi {router_instanceabi}")
        router_instance = ex.eth.contract(address=ex.to_checksum_address(router), abi=router_instanceabi) #ContractLiquidityRouter
        if (dex_version=="v3"):
            quoter_instanceabi= await fetch_abi_dex(quoter_instance) #Quoter ABI
            quoter_instance = ex.eth.contract(address=ex.to_checksum_address(quoter_instanceabi), abi=quoter_instanceabi) #ContractLiquidityQuoter
        try:
            ex.net.listening
            logger.info(msg=f"connected to {ex}")
            return ex_name
        except Exception as e:
            await handle_exception(e)
    elif ('api' in ex_result):
        ex_name = ex_result['name']
        chainId= 0
        client = getattr(ccxt, ex_name)
        try:
            ex = client({'apiKey': ex_result['api'],'secret': ex_result['secret']})
            price_type=ex_result['ordertype']
            if (ex_result['testmode']=='True'):
                logger.info(msg=f"sandbox setup")
                ex.set_sandbox_mode('enabled')
            markets= ex.loadMarkets()
            return ex
        except Exception as e:
            await handle_exception(e)
    else:
        return

#📦ORDER
async def execute_order(direction,symbol,stoploss,takeprofit,quantity):
    if (bot_trading_switch == False):
        logger.info(msg=f"TRADING is {bot_trading_switch}")
        return
    try:
        if not isinstance(ex,web3.main.Web3):
            logger.debug(msg=f"cex order: {direction} {symbol} {stoploss} {takeprofit} {quantity}")
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            if (len(str(bal))):
                m_price = float(ex.fetchTicker(f'{symbol}').get('last'))
                totalusdtbal = ex.fetchBalance()['USDT']['free']
            amountpercent=((totalusdtbal)*(float(quantity)/100))/float(m_price) # % of bal
            res = ex.create_order(symbol, price_type, direction, amountpercent)
            if (direction=="SELL"):
                response = f"⬇️ {symbol}"
            else:
                response = f"⬆️ {symbol}"
            response+= f"\n➕ Size: {res['amount']}\n⚫️ Entry: {res['price']}\nℹ️ {res['id']}\n🗓️ {res['datetime']}"

        elif (isinstance(ex,web3.main.Web3)):
     
            asset_out_symbol = basesymbol if direction=="BUY" else symbol
            asset_in_symbol = symbol if direction=="BUY" else basesymbol
            response = f"⬆️ {asset_in_symbol}" if direction=="BUY" else f"⬇️ {asset_out_symbol}"
            asset_out_address= await search_gecko_contract(asset_out_symbol)
            asset_out_abi= await fetch_abi_dex(asset_out_address)
            asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            asset_in_address= await search_gecko_contract(asset_in_symbol)
            order_path_dex=[asset_out_address, asset_in_address]
            asset_out_decimals=asset_out_contract.functions.decimals().call()
            asset_out_balance=fetch_user_token_balance(asset_out_symbol)
            if (asset_out_balance <=0):
                msg=f"Balance for {asset_out_symbol} is {asset_out_balance}"
                await handle_exception(msg)
                return
            asset_out_amount = ((asset_out_balance)/(10 ** asset_out_decimals))*(float(quantity)/100) #buy %p ercentage  
            #asset_out_amount = (asset_out_balance)/(10 ** asset_out_decimals) #SELL all token in case of sell order
            asset_out_amount_converted = (ex.to_wei(asset_out_amount,'ether'))
            slippage=2# max 2% slippage
            transaction_amount = (asset_out_amount_converted *(slippage/100)) 
            deadline = ex.eth.get_block("latest")["timestamp"] + 3600 # or deadline = (int(time.time()) + 1000000)
            if (dex_version=='uni_v2'): #https://docs.uniswap.org/contracts/v2/reference/smart-contracts/router-02
                await approve_asset_router(asset_out_address)
                transaction_getoutput_amount  = router_instance.functions.getOutputAmount(transaction_amount, order_path_dex).call()
                transaction_minimum_amount = int(transaction_getoutput_amount[1])
                swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_minimum_amount,order_path_dex,walletaddress,deadline)
                tx_token = await sign_transaction_dex(swap_TX)

            elif (dex_version=="1inch_v5.0"): #https://docs.1inch.io/docs/aggregation-protocol/api/swagger/#
                await approve_asset_router(asset_out_address)
                swap_url = f"{dex_1inch_api}/{chainId}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={walletaddress}&slippage={slippage}"
                swap_TX = await retrieve_url_json(swap_url)
                tx_token= await sign_transaction_dex(swap_TX)

            elif (dex_version=="uni_v3"):  # https://docs.uniswap.org/contracts/v3/guides/swaps/single-swaps
                await approve_asset_router(asset_out_address)
                sqrtPriceLimitX96 = 0
                fee = 3000
                transaction_minimum_amount = self.quoter.functions.quoteExactInputSingle(asset_out_address, asset_in_address, fee, transaction_amount, sqrtPriceLimitX96).call()
                swap_TX = router_instance.functions.exactInputSingle(asset_in_address,asset_out_address,fee,walletaddress,deadline,transaction_amount,transaction_minimum_amount,sqrtPriceLimitX96)
                tx_token = await sign_transaction_dex(swap_TX)

            elif (dex_version =="1inch_LimitOrder_v2"): #https://docs.1inch.io/docs/limit-order-protocol/smart-contract/LimitOrderProtocol
                return
            txHash = str(ex.to_hex(tx_token))
            txResult = await fectch_transaction_dex(txHash)
            txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
            if(txResult == "1"):
                response+= f"\n➕ Size: {round(ex.from_wei(transaction_amount, 'ether'),5)}\n⚫️ Entry: {await fetch_gecko_asset_price(asset_in_address)}USD \nℹ️ {txHash}\n⛽️ {txHashDetail['gasUsed']}\n🗓️ {datetime.now()}"
                logger.info(msg=f"{response}")

        return response

    except Exception as e:
        await handle_exception(e)
        return

#🦄DEX
async def resolve_ens_dex(addr):
    try:
        #pending middleware approach for implementation WIP
        domain = ns.name(addr)
        logger.info(msg=f"{domain}")
        return
    except Exception as e:
        await handle_exception(e)

async def approve_asset_router(asset_out_address):
    try:
        if (dex_version=="uni_v2" or dex_version=="uni_v3"):
            approval_check = asset_out_contract.functions.allowance(ex.to_checksum_address(walletaddress), ex.to_checksum_address(router)).call()
            logger.info(msg=f"approval_check {approval_check}")
            if (approval_check==0):
                approved_amount = (ex.to_wei(2**64-1,'ether'))
                asset_out_abi = await fetch_abi_dex(asset_out_address)
                asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(ex.to_checksum_address(router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                time.sleep(10) #wait approval
        if (dex_version=="1inch_v5"):
            approval_check_URL = f"{dex_1inch_api}/{chainId}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={walletaddress}"
            approval_response = await retrieve_url_json(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check==0):
                approval_URL = f"{dex_1inch_api}/{chainId}/approve/transaction?tokenAddress={asset_out_address}"
                approval_response = await retrieve_url_json(approval_URL)
    except Exception as e:
        await handle_exception(e)


async def sign_transaction_dex(contract_tx):
    try:
        if (dex_version=='uni_v2'):
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
        elif (dex_version=="uni_v3"):
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
        elif (dex_version=="1inch_v5"):
            tx_params = {
            'nonce': ex.eth.get_transaction_count(walletaddress),
            'gas': int(gasLimit),
            'gasPrice': ex.to_wei(gasPrice,'gwei'),
            }
            tx = contract_tx.build_transaction(tx_params)
            signed = ex.eth.account.sign_transaction(tx, privatekey)
            raw_tx = signed.rawTransaction
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
        resp = await retrieve_url_json(url, params)
        logger.debug(msg=f"resp {resp}")
        abi = resp["result"]
        logger.debug(msg=f"abi {abi}")
        if(abi!=""):
            return abi
        else:
            return None
    except Exception as e:
        await handle_exception(e)

async def fectch_transaction_dex (txHash):
    checkTransactionSuccessURL = abiurl + "?module=transaction&action=gettxreceiptstatus&txhash=" + txHash + "&apikey=" + abiurltoken
    checkTransactionRequest =  await retrieve_url_json(checkTransactionSuccessURL)
    txResult = checkTransactionRequest['status']
    return txResult

async def fetch_1inch_quote(token):
    asset_in_address = await search_gecko_contract(token)
    asset_out_address = await search_gecko_contract('USDC')
    try:
        asset_out_amount=1000000000000
        quote_url = f"{dex_1inch_api}/{chainId}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
        quote_response = requests.get(quote_url)
        quote = quote_response.json()
        logger.debug(msg=f"quote {quote}")
        asset_out_1inch_quote = quote['toTokenAmount']
        return asset_out_1inch_quote
    except Exception:
        return

async def fetch_oracle_quote(token):
    try:
        return
    except Exception:
        return

async def fetch_user_token_balance(token):
    try:
        token_address= await search_gecko_contract(token)
        token_abi= await fetch_abi_dex(asset_out_address)
        token_contract = ex.eth.contract(address=token_address, abi=token_abi)
        token_balance=asset_out_contract.functions.balanceOf(walletaddress).call()
        if ((token_balance <=0) or token_balance==None):
            return 0
        return token_balance
    except Exception:
        return 0

async def fetch_account_dex (addr):
    url = abiurl
    query = {'module':'account',
            'action':'tokenbalance',
            'contractaddress':addr,
            'address':walletaddress,
            'tag':'latest',
            'apikey':abiurltoken}
    r = requests.get(url, params=query)
    try:
        d = json.loads(r.text)
    except:
        return None
    value = int(d['result']) / self.zeroes
    return(value)

async def estimate_gas(transaction):
    estimate_gas_cost = int(ex.to_wei(ex.eth.estimate_gas(transaction) * 1.2),'wei')
    

async def verify_gas():
    current_gas_price = int(ex.to_wei(ex.eth.gas_price,'wei'))
    config_gas_price_dex = int(ex.to_wei(gasPrice,'gwei'))
    if (current_gas_price_dex>=config_gas_price_dex):
        logger.warning(msg=f"{current_gas_price_dex} {config_gas_price_dex} ")
    else:
        logger.info(msg=f"gas setup{config_gas_price_dex} aligned with current gas price {current_gas_price_dex}")

#🦎GECKO
async def search_gecko(token):
    try:
        symbol_info = gecko_api.search(query=token)
        #logger.info(msg=f"symbol_info {symbol_info}")
        for i in symbol_info['coins']:
            results_search_coin = i['symbol']
            if (results_search_coin==token.upper()):
                api_symbol = i['api_symbol']
                logger.debug(msg=f"api info {api_symbol}")
                return api_symbol
    except Exception:
        return

async def search_gecko_detailed(token):
    try:
        coin_info = gecko_api.get_coin_by_id(await search_gecko(token))
        #logger.debug(msg=f"coin_info {coin_info}")
        coin_symbol= coin_info['symbol']
        coin_platform = coin_info['asset_platform_id']
        coin_image = coin_info['image']['small']
        coin_link = coin_info['links']['homepage'][0]
        coin_price = coin_info['market_data']['current_price']['usd']
        response = f'Symbol {coin_symbol}\nPlatform {coin_platform}\nPrice: {coin_price}USD\nmore info {coin_link} {coin_image}'
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

async def search_gecko_contract(token):
    try:
        coin_info = gecko_api.get_coin_by_id(id=f'{await search_gecko(token)}')
        logger.debug(msg=f"coin_info {coin_info}")
        coin_contract = coin_info['platforms'][f'{await search_gecko_platform()}']
        logger.info(msg=f"search gecko contract {token} {coin_contract}")
        return ex.to_checksum_address(coin_contract)
    except Exception:
        return

async def fetch_gecko_asset_price(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{await search_gecko_platform()}',contract_address=asset_in_address)
        logger.debug(msg=f"fetch_tokeninfo{fetch_tokeninfo}")
        asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
        return asset_out_cg_quote
    except Exception as e:
        print(f"An error occurred while retrieving address {e}")

async def fetch_gecko_quote(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{await search_gecko_platform()}',contract_address=asset_in_address)
        logger.debug(msg=f"fetch_tokeninfo{fetch_tokeninfo}")
        asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
        asset_out_cg_name = fetch_tokeninfo['name']
        response = f"{asset_out_cg_name}\n🦎{asset_out_cg_quote} USD"
        return response
    except Exception:
        return

#🔒PRIVATE
async def get_account_balance():
    try:
        msg = ""
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
            basesymbol_bal = round(ex.from_wei(await fetch_user_token_balance(basesymbol),'ether'),5)
            msg += f"\n💲{bal} \n💵{basesymbol_bal} {basesymbol}"
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
"""
🔚END OF COMMON FUNCTIONS
"""

#🦾BOT COMMAND

fullcommandlist = """
🏦<code>/bal</code>

🏛️ <code>/cex kraken</code>
🥞 <code>/dex pancake</code>
🦄 <code>/dex uniswap_v2</code>

📦
<code>buy btc/usdt sl=1000 tp=20 q=1%</code>
<code>buy cake</code>

🦎
<code>/q BTCB</code> 
<code>/q WBTC</code> 
<code>/q btc/usdt</code>

🔀
<code>/trading</code>
<code>/testmode</code>"""
bot_menu_help = f"{TTversion} \n {fullcommandlist}"

async def post_init(application: Application):
    message=f"Bot is online {TTversion}"
    await load_exchange(ex_name)
    await application.bot.send_message(bot_channel_id, message, parse_mode=constants.ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_ping = await verify_latency_ex()
    msg= f"Environment: {defaultenv} Ping: {bot_ping}ms\nExchange: {ex_name} Sandbox: {ex_test_mode}\n{bot_menu_help}"
    await send(update,msg)

async def account_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    balance =f"🏦 Balance"
    balance += await get_account_balance()
    await send(update,balance)

async def order_scanner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_message = update.effective_message.text
    order = await parse_message(channel_message)
    if (order):
        try:
            res = await execute_order(order[0],order[1],order[2],order[3],order[4])
            if (res != None):
                response = f"{res}"
                await send(update,response)
        except Exception as e:
            await handle_exception(e)
            return

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol = await parse_message(update.effective_message.text)
    asset_out_cg_quote = await fetch_gecko_quote(symbol)
    response=f"₿ {asset_out_cg_quote}\n"
    if (isinstance(ex,web3.main.Web3)):
        if(await search_gecko_contract(symbol) != None):
            asset_out_1inch_quote = await fetch_1inch_quote (symbol)
            response+=f"🦄{asset_out_1inch_quote} USD\n🖊️{chainId}: {await search_gecko_contract(symbol)}"
    elif not (isinstance(ex,web3.main.Web3)):
        price= ex.fetch_ticker(symbol.upper())['last']
        response+=f"🏛️ {price} USD"
    await send(update,response)

async def get_tokeninfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    symbol= await parse_message(update.effective_message.text)
    gecko_symbol_info = await search_gecko_detailed(symbol)
    logger.info(msg=f"token info for {symbol}\n {gecko_symbol_info}")
    await send(update,gecko_symbol_info)

async def exchange_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_exchange = await parse_message(update.effective_message.text)
    res = await load_exchange(new_exchange['name'])
    response = f"{ex_name} is active"
    await send(update,response)

async def trading_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    message=f"Trading is {bot_trading_switch}"
    await send(update,message)

async def testmode_switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global ex_test_mode
    ex_test_mode = not ex_test_mode
    message = f"Test mode is {ex_test_mode}"
    await send(update, message)

async def restart_command(application: Application, update: Update) -> None:
    logger.info(msg=f"restarting ")
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

async def stop_command(self) -> None:
    if self.application is None or self.application.updater is None:
        return
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e = f"{tb_trim}"
    await handle_exception(e)

#💾DB
db_url=os.getenv("DB_URL")
if db_url == None:
    logger.info(msg = f"No remote DB")
else:
    outfile = os.path.join('./config', 'db.json')
    response = requests.get(db_url, stream=True)
    logger.debug(msg=f"{response}")
    with open(outfile,'wb') as output:
      output.write(response.content)
      logger.debug(msg = f"copied the remote DB")
      
db_path = './config/db.json'
if os.path.exists(db_path):
    logger.debug(msg=f"Existing DB")
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
        logger.debug(msg=f"{bot}")
        bot_token = bot[0]['token']
        bot_channel_id = bot[0]['channel']
        bot_webhook_port = bot[0]['port']
        bot_webhook_secret = bot[0]['secret_token']
        bot_webhook_privatekey = bot[0]['key']
        bot_webhook_certificate = bot[0]['cert']
        bot_webhook_url = bot[0]['webhook_url']
        bot_trading_switch = True
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
        logger.warning(msg=f"error with db file {db_path}, verify Json. error: {e}")

#🤖BOT
def main():
    try:
        verify_import_library()

#Starting Bot
        application = Application.builder().token(bot_token).post_init(post_init).build()
#BotMenu
        application.add_handler(MessageHandler(filters.Regex('/help'), help_command))
        application.add_handler(MessageHandler(filters.Regex('/bal'), account_balance_command))
        application.add_handler(MessageHandler(filters.Regex('/q'), quote_command))
        application.add_handler(MessageHandler(filters.Regex('/trading'), trading_switch_command))
        application.add_handler(MessageHandler(filters.Regex('(?:cex|dex)'), exchange_switch_command))
        application.add_handler(MessageHandler(filters.Regex('(?:buy|Buy|BUY|sell|Sell|SELL)'), order_scanner))
        application.add_handler(MessageHandler(filters.Regex('/testmode'), testmode_switch_command))
        application.add_handler(MessageHandler(filters.Regex('/coin'), get_tokeninfo_command))
        application.add_handler(MessageHandler(filters.Regex('/t1'), search_gecko))
        application.add_handler(MessageHandler(filters.Regex('/restart'), restart_command))
        application.add_error_handler(error_handler)
#Run the bot
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.info(msg="Bot failed to start. Error: " + str(e))


if __name__ == '__main__':
    main()
