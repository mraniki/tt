##=============== VERSION =============

TTversion="🪙🗿 TT Beta 1.3.1"

##=============== import  =============
##log
import logging
import sys
##env
import os
from dotenv import load_dotenv
import json, requests
import asyncio
import re

#Utils
from pycoingecko import CoinGeckoAPI
from ping3 import ping
from ttp import ttp

#db
from tinydb import TinyDB, Query, where
#CEX
import ccxt
#DEX
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from datetime import datetime
from dxsp import DexSwap

#messaging platform
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

#API
from fastapi import FastAPI, Header, HTTPException, Request
import uvicorn
import http

#🔧CONFIG
load_dotenv()

#🧐LOGGING
LOGLEVEL=os.getenv("LOGLEVEL", "INFO")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info(msg=f"LOGLEVEL {LOGLEVEL}")
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

#🔗API
gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup
dex_1inch_api = "https://api.1inch.exchange/v5.0"
dex_1inch_limit_api = "https://limit-orders.1inch.io/v3.0"
dex_0x_api = "https://api.0x.org/orderbook/v1"

#🔁UTILS
async def verify_import_library():
    logger.info(msg=f"{TTversion}")


async def parse_message(self,msg):
    logger.debug(msg=f"self {self} msg {msg}")
    if bot_service == 'tgram':
        msg=self.effective_message.text
        logger.debug(msg=f"content {self['channel_post']['text']}")
    if not msg:
        return
    wordlist = msg.split(" ")
    wordlistsize = len(wordlist)
    logger.debug(msg=f"parse_message wordlist {wordlist} len {wordlistsize}")
    try:
        logger.debug(msg="orderparsing NEW")
        orderparsing = await order_parsing(msg)
        logger.debug(msg="orderparsing COMPLETED")
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
        'exchange_switch': ['/cex', '/dex', '/cext', '/dext']
    }
    try:
        for name, keywords in filters.items():
            if any(keyword in wordlist for keyword in keywords):
                if name == 'balance':
                    response = await account_balance_command()
                elif name == 'exchange_switch':
                    response = await exchange_switch_command(wordlist[1])
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
                elif name == 'test_mode':
                    response = await testmode_switch_command()
                elif name == 'trading':
                    response = await trading_switch_command()
                if response:
                    await notify(response)
    except Exception:
        logger.warning(msg="Parsing exception")

async def order_parsing(message_to_parse):
    logger.info(msg=f"order_parsing V2 with {message}")
    try:
        order_template = """ {{ direction }} {{ symbol }} sl={{ stoploss }} tp={{ takeprofit }} q={{ quantity }} """
        parser = ttp(data=message_to_parse, template=order_template)
        parser.parse()
        result = parser.result(format="json")
        print(result[0])
    except Exception as e:
        logger.warning(msg=f"Order parsing error {e}")

async def retrieve_url_json(url,params=None):
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url,params =params,headers=headers)
    logger.debug(msg=f"retrieve_url_json {response}")
    return response.json()

async def verify_latency_ex():
    try:
        return (
            round(ping(ex_node_provider, unit='ms'), 3)
            if isinstance(ex, web3.main.Web3)
            else round(ping("1.1.1.1", unit='ms'), 3)
        )
    except Exception as e:
        logger.warning(msg=f"Latency error {e}")

#💬MESSAGING
async def notify(msg):
    if not msg:
        return
    apobj = apprise.Apprise()
    if bot_service in ['tgram', 'telethon']:
        apobj.add(f'tgram://{str(bot_token)}/{str(bot_channel_id)}')
    elif (bot_service =='discord'):
        apobj.add(f'{bot_service}://{str(bot_webhook_id)}/{str(bot_webhook_token)}')
    elif (bot_service =='matrix'):
        apobj.add(f"matrixs://{bot_user}:{bot_pass}@{bot_hostname[8:]}:443/{str(bot_channel_id)}")
    try:
        await apobj.async_notify(body=msg, body_format=NotifyFormat.HTML)
    except Exception as e:
        logger.warning(msg=f"{msg} not sent due to error: {e}")

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
    global block_explorer_url
    global block_explorer_api
    global basesymbol
    global gasPrice
    global gasLimit
    global router_instance
    global router_instanceabi
    global coin_platform
    global ns

    logger.info(msg=f"Setting up {exchangeid}")
    ex_result = await search_exchange(exchangeid)
    exchange_info = await search_gecko_exchange(exchangeid)
    logger.debug(msg=f"exchange_info {exchange_info}")
    if ('router' in ex_result):
        ex_name = ex_result['name']
        ex_test_mode=ex_result['testmode']
        ex_node_provider= ex_result['networkprovider']
        router= ex_result['router']
        block_explorer_url=ex_result['block_explorer_url']
        block_explorer_api=ex_result['block_explorer_api']
        basesymbol=ex_result['basesymbol']
        dex_version= ex_result['version']
        gasLimit=ex_result['gasLimit']
        gasPrice=ex_result['gasPrice']
        chain_id=ex_result['chainId']
        wallet_address= ex_result['walletaddress']
        private_key= ex_result['privatekey']


        dex = DexSwap(chain_id=chain_id,wallet_address=wallet_address,private_key=private_key,block_explorer_api=block_explorer_api)
        logger.info(msg=f"dexswap object dex {dex}")
        

        ex = Web3(Web3.HTTPProvider(f'https://{ex_node_provider}'))
        coin_platform = await search_gecko_platform()
        router_instanceabi= await fetch_abi_dex(router)
        logger.info(msg=f"router_instanceabi {router_instanceabi}")
        router_instance = ex.eth.contract(address=ex.to_checksum_address(router), abi=router_instanceabi)
        try:
            ex.net.listening
            logger.info(msg=f"connected to {ex}")
            return ex_name
        except Exception as e:
            await handle_exception(e)

    elif ('api' in ex_result):
        ex_name = ex_result['name']
        defaultType =  ex_result['defaultType'],
        chainId = 0
        client = getattr(ccxt, ex_name)
        try:
            if (defaultType=="SPOT"):
                ex = client({'apiKey': ex_result['api'],'secret': ex_result['secret'], })
            else:
                ex = client({'apiKey': ex_result['api'],'secret': ex_result['secret'],'options': {'defaultType': ex_result['defaultType'],    }, })
            price_type=ex_result['ordertype']
            if (ex_result['testmode']=='True'):
                logger.info(msg="sandbox setup")
                ex.set_sandbox_mode('enabled')
            markets = ex.load_markets()
            return ex
        except Exception as e:
            await handle_exception(e)
    else:
        return

#📦ORDER
async def execute_order(direction,symbol,stoploss,takeprofit,quantity):
    if bot_trading_switch == False:
        return

    try:
        response = f"⬇️ {symbol}" if (direction=="SELL") else f"⬆️ {symbol}"
        if not isinstance(ex,web3.main.Web3):
            if (await get_account_balance()=="No Balance"): 
                await handle_exception("Check your Balance")
                return
            asset_out_quote = float(ex.fetchTicker(f'{symbol}').get('last'))
            totalusdtbal = await get_account_basesymbol_balance() ##ex.fetchBalance()['USDT']['free']
            amountpercent = (totalusdtbal)*(float(quantity)/100) / asset_out_quote
            order = ex.create_order(symbol, price_type, direction, amountpercent)
            response+= f"\n➕ Size: {order['amount']}\n⚫️ Entry: {order['price']}\nℹ️ {order['id']}\n🗓️ {order['datetime']}"
        else:
            order = execute_order.dex(direction,symbol,stoploss,takeprofit,quantity)
            # response+= f"\n➕ Size: {order['amount']}\n⚫️ Entry: {order['price']}\nℹ️ {order['id']}\n🗓️ {order['datetime']}"

            # asset_out_symbol = basesymbol if direction=="BUY" else symbol
            # asset_in_symbol = symbol if direction=="BUY" else basesymbol
            # response = f"⬆️ {asset_in_symbol}" if direction=="BUY" else f"⬇️ {asset_out_symbol}"
            # logger.debug(msg=f"asset_out_symbol {asset_out_symbol} asset_in_symbol {asset_in_symbol}")
            # asset_out_address= await search_contract(asset_out_symbol)
            # if asset_out_address is None:
            #     await handle_exception(f"{asset_out_symbol} not supported")
            #     return
            # asset_out_abi= await fetch_abi_dex(asset_out_address)
            # asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            # asset_in_address= await search_contract(asset_in_symbol)
            # if asset_in_address is None:
            #     await handle_exception(f"{asset_in_symbol} not supported")
            #     return
            # logger.debug(msg=f"asset_out_address {asset_out_address} asset_in_address {asset_in_address}")
            # order_path_dex=[asset_out_address, asset_in_address]
            # asset_out_decimals=asset_out_contract.functions.decimals().call()
            # asset_out_balance = await fetch_token_balance(asset_out_symbol)
            # if (asset_out_balance <=0):
            #     await handle_exception(f"Balance for {asset_out_symbol} is {asset_out_balance}")
            #     return
            # if direction=="BUY":
            #     asset_out_amount = ((asset_out_balance)/(10 ** asset_out_decimals))*(float(quantity)/100) #buy %p ercentage
            # if direction=="SELL":
            #     asset_out_amount = (asset_out_balance)/(10 ** asset_out_decimals) #SELL all token in case of sell order
            # asset_out_amount_converted = (ex.to_wei(asset_out_amount,'ether'))
            # slippage=2# max 2% slippage
            # transaction_amount = int((asset_out_amount_converted *(slippage/100))) 
            # deadline = ex.eth.get_block("latest")["timestamp"] + 3600
            # logger.error(msg=f"asset_out_amount {asset_out_amount}  asset_out_amount_converted {asset_out_amount_converted} transaction_amount {transaction_amount}")
            # if dex_version == 'uni_v2': 
            #     await approve_asset_router(asset_out_address,asset_out_contract)
            #     transaction_min_amount  = int(router_instance.functions.getAmountsOut(transaction_amount, order_path_dex).call()[1])
            #     swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_min_amount,order_path_dex,walletaddress,deadline)
            #     tx_token = await sign_transaction_dex(swap_TX)
            # elif dex_version == '1inch_v5': 
            #     await approve_asset_router(asset_out_address,asset_out_contract)
            #     swap_url = f"{dex_1inch_api}/{chainId}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={walletaddress}&slippage={slippage}"
            #     swap_TX = await retrieve_url_json(swap_url)
            #     tx_token= await sign_transaction_dex(swap_TX)
            # else:
            #     logger.error(msg=f"dex_version not supported {dex_version}")
            #     return
            # txHash = str(ex.to_hex(tx_token))
            # txResult = await fectch_transaction_dex(txHash)
            # txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
            # if(txResult == "1"):
            #     response+= f"\n➕ Size: {round(ex.from_wei(transaction_amount, 'ether'),5)}\n⚫️ Entry: {await fetch_gecko_asset_price(asset_in_symbol)}USD \nℹ️ {txHash}\n⛽️ {txHashDetail['gasUsed']}\n🗓️ {datetime.now()}"
            #     logger.info(msg=f"{response}")
        return response

    except Exception as e:
        logger.error(msg=f"Exception with order processing {e}")
        await handle_exception(e)
        return

#🦄DEX

async def execute_order_dex(direction,symbol,stoploss,takeprofit,quantity):
    try:
        return
    except Exception as e:
        await handle_exception(e)



async def approve_asset_router(asset_out_address,asset_out_contract):
    try:
        if dex_version in ["uni_v2", "uni_v3"]:
            approval_check = asset_out_contract.functions.allowance(ex.to_checksum_address(walletaddress), ex.to_checksum_address(router)).call()
            logger.debug(msg=f"approval_check {approval_check}")
            if (approval_check==0):
                approved_amount = (ex.to_wei(2**64-1,'ether'))
                asset_out_abi = await fetch_abi_dex(asset_out_address)
                asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
                approval_TX = asset_out_contract.functions.approve(ex.to_checksum_address(router), approved_amount)
                approval_txHash = await sign_transaction_dex(approval_TX)
                approval_txHash_complete = ex.eth.wait_for_transaction_receipt(approval_txHash, timeout=120, poll_latency=0.1)
        if (dex_version=="1inch_v5"):
            approval_check_URL = f"{dex_1inch_api}/{chainId}/approve/allowance?tokenAddress={asset_out_address}&walletAddress={walletaddress}"
            approval_response = await retrieve_url_json(approval_check_URL)
            approval_check = approval_response['allowance']
            if (approval_check==0):
                approval_URL = f"{dex_1inch_api}/{chainId}/approve/transaction?tokenAddress={asset_out_address}"
                approval_response = await retrieve_url_json(approval_URL)
    except Exception as e:
        logger.debug(msg=f"approve_asset_router error {e}")
        await handle_exception(e)

async def sign_transaction_dex(tx):
    logger.debug(msg=f"✍️ sign_transaction_dex {tx}")
    try:
        if dex_version in ['uni_v2']:
            tx_params = {
            'from': walletaddress,
            'gas': int(gasLimit),
            'gasPrice': ex.to_wei(gasPrice,'gwei'),
            'nonce': ex.eth.get_transaction_count(walletaddress),
            }
            tx = tx.build_transaction(tx_params)
        if dex_version in ['uni_v3']:
            tx_params = {
            'from': walletaddress,
            'gas': await estimate_gas(tx),
            'gasPrice': ex.to_wei(gasPrice,'gwei'),
            'nonce': ex.eth.get_transaction_count(walletaddress),
            }
            tx = tx.build_transaction(tx_params)
        elif dex_version == "1inch_v5":
            tx = tx['tx']
            tx['to'] = ex.to_checksum_address(tx['to'])
            tx['gas'] = await estimate_gas(tx)
            tx['nonce'] = ex.eth.get_transaction_count(walletaddress)
            tx['value'] = int(tx['value'])
            tx['gasPrice'] = int(ex.to_wei(gasPrice,'gwei'))
        signed = ex.eth.account.sign_transaction(tx, privatekey)
        raw_tx = signed.rawTransaction
        return ex.eth.send_raw_transaction(raw_tx)
    except Exception as e:
        logger.debug(msg=f"sign_transaction_dex contract {tx} error {e}")
        await handle_exception(e)
        return

async def fetch_abi_dex(addr):
    try:
        url = block_explorer_url
        logger.debug(msg=f"fetch_abi_dex url {url}")
        params = {
            "module": "contract",
            "action": "getabi",
            "address": addr,
            "apikey": block_explorer_api }
        resp = await retrieve_url_json(url, params)
        abi = resp["result"]
        #logger.debug(msg=f"abi {abi}")
        return abi if (abi!="") else None
    except Exception as e:
        await handle_exception(e)

async def fectch_transaction_dex (txHash):
    checkTransactionSuccessURL = f"{block_explorer_url}?module=transaction&action=gettxreceiptstatus&txhash={txHash}&apikey={block_explorer_api}"
    checkTransactionRequest =  await retrieve_url_json(checkTransactionSuccessURL)
    return checkTransactionRequest['status']

async def fetch_1inch_quote(token):
    asset_in_address = await search_contract(token)
    asset_out_address = await search_contract('usdc')
    try:
        asset_out_amount=1000000000000
        quote_url = f"{dex_1inch_api}/{chainId}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
        quote = retrieve_url_json(quote_url)
        logger.debug(msg=f"quote {quote}")
        return quote['toTokenAmount']
    except Exception:
        return

async def estimate_gas(tx):
    return int(ex.to_wei(ex.eth.estimate_gas(tx) * 1.25,'wei'))

async def fetch_account_dex(addr):
    url = block_explorer_url
    query = {'module':'account',
            'action':'tokenbalance',
            'contractaddress':addr,
            'address':walletaddress,
            'tag':'latest',
            'apikey':block_explorer_api}
    r = requests.get(url, params=query)
    try:
        d = json.loads(r.text)
    except:
        return None
    return int(d['result']) / self.zeroes

async def search_test_contract(symbol):
    logger.info(msg=f"📝search_test_contract {symbol} and chainId {chainId}")
    try:
        tokenlist=os.getenv("TESTTOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/testnet.json")
        token_list = await retrieve_url_json(tokenlist)
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and keyval['chainId'] == int(chainId)):
                logger.info(msg=f"address {keyval['address']}")
                symbolcontract = keyval['address']
        logger.info(msg=f"📝 contract  {symbolcontract}")
        if symbolcontract:
            return symbolcontract
    except Exception as e:
        logger.error(msg=f"search_test_contract error {token}")
        await HandleExceptions(e)
        return

async def search_json_contract(symbol):
    logger.info(msg=f"📝search_contract {symbol} and chainId {chainId}")
    try:
        alltokenlist=os.getenv("TOKENLIST", "https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json") #https://raw.githubusercontent.com/viaprotocol/tokenlists/main/all_tokens/all.json
        token_list = await retrieve_url_json(alltokenlist)
        logger.info(msg=f"token_list {token_list}")
        token_search = token_list['tokens']
        for keyval in token_search:
            if (keyval['symbol'] == symbol and keyval['chainId'] == int(chainId)):
                logger.info(msg=f"address {keyval['address']}")
                return keyval['address']
    except Exception as e:
        logger.error(msg=f"search_json_contract error {symbol} {e}")


async def search_contract(token):
    try:
        token_contract = dex.search_contract(token)
        logger.error(msg=f"dex contract {contract}")
        
        # if ex_test_mode == 'True':
        #     token_contract = await search_test_contract(token)
        # else:
        #     token_contract = await search_json_contract(token)
        #     logger.error(msg=f"search_contract token_contract {token_contract}")
        # if token_contract is None:
        #     token_contract = await search_gecko_contract(token)
        if token_contract:
            return ex.to_checksum_address(token_contract)
    except Exception as e:
        logger.error(msg=f"search_contract error {token} {e}")

#🦎GECKO
async def search_gecko_contract(token):
    try:
        coin_info = await search_gecko(token)
        coin_contract = coin_info['platforms'][f'{coin_platform}']
        logger.info(msg=f"🦎 contract {token} {coin_contract}")
        return ex.to_checksum_address(coin_contract)
    except Exception:
        return

async def search_gecko(token):
    try:
        search_results = gecko_api.search(query=token)
        search_dict = search_results['coins']
        filtered_dict = [x for x in search_dict if x['symbol'] == token.upper()]
        api_dict = [ sub['api_symbol'] for sub in filtered_dict ]
        for i in api_dict:
            coin_dict = gecko_api.get_coin_by_id(i)
            try:
                if coin_dict['platforms'][f'{coin_platform}'] is not None:
                    return coin_dict
            except KeyError:
                pass
    except Exception as e:
        logger.error(msg=f"search_gecko error {e}")
        return

async def search_gecko_platform():
    try:
        assetplatform = gecko_api.get_asset_platforms()
        output_dict = [x for x in assetplatform if x['chain_identifier'] == int(chainId)]
        return output_dict[0]['id']
    except Exception as e:
        logger.debug(msg=f"search_gecko_platform error {e}")

async def search_gecko_exchange(exchange):
    try:
        exchange_list = gecko_api.get_exchanges_list()
        for i in exchange_list:
            results_search_exchange = i['id']
            if (results_search_exchange == exchange):
                return i
    except Exception:
        return

async def fetch_gecko_asset_price(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{coin_platform}',contract_address=asset_in_address)
        return fetch_tokeninfo['market_data']['current_price']['usd']
    except Exception:
        return

async def fetch_gecko_quote(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{coin_platform}',contract_address=asset_in_address)
        logger.debug(msg=f"fetch_tokeninfo {fetch_tokeninfo}")
        asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
        asset_out_cg_name = fetch_tokeninfo['name']
        return f"{asset_out_cg_name}\n🦎{asset_out_cg_quote} USD"
    except Exception:
        return

#🔒PRIVATE
async def get_account_balance():
    try:
        if not isinstance(ex,web3.main.Web3):
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            sbal = "".join(f"{iterator}: {value} \n" for iterator, value in bal.items())
            if not sbal:
                sbal = "No Balance"
            msg = f"{sbal}"
        else:
            bal = get_account_balance.dex()
            msg = {bal}

        return msg
    except Exception:
        return

async def fetch_token_balance(token):
    try:
        if not isinstance(ex, web3.main.Web3):
            return ex.fetch_free_balance()[f'{token}']
        token_address= await search_contract(token)
        token_abi= await fetch_abi_dex(token_address)
        token_contract = ex.eth.contract(address=token_address, abi=token_abi)
        token_balance=token_contract.functions.balanceOf(walletaddress).call()
        logger.debug(msg=f"token_address {token_address} token_balance {token_balance}")
        return 0 if token_balance <=0 or token_balance is None else token_balance
    except Exception as e:
        logger.error(msg=f"{token} balance error: {e}")
        return 0

async def get_account_basesymbol_balance():
    try:
        if isinstance(ex, web3.main.Web3):
            return round(ex.from_wei(await fetch_token_balance(basesymbol), 'ether'), 5)
        else:
            return ex.fetchBalance()['USDT']['free']
    except Exception:
        await handle_exception("Check your balance")

async def get_account_position():
    try:
        logger.debug(msg="get_account_position")
        if not isinstance(ex,web3.main.Web3):
            positions = ex.fetch_positions()
            open_positions = [p for p in positions if p['type'] == 'open']
        else:
            # asset_position_address= await search_contract(asset_out_symbol)
            # asset_position_abi= await fetch_abi_dex(asset_out_address)
            # asset_position_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            # open_positions = asset_position_contract.functions.getOpenPositions(walletaddress).call()
            open_positions = "DEX POS WiP"
        logger.debug(msg=f"open_positions {open_positions}")
        return open_positions or 0
    except Exception:
        await handle_exception("Error when retrieving position")


async def get_account_margin():
    try:
        return
    except Exception as e:
        await handle_exception(e)
        return

async def get_wallet_auth():
    try:
        return
    except Exception as e:
        await handle_exception(e)
        return

#======= error handling
async def handle_exception(e) -> None:
    try:
        msg = ""
        logger.error(msg=f"error: {e}")
    except KeyError:
        msg = "DB content error"
        sys.exit()
    except telegram.error:
        msg = "telegram error"
    except ConnectionError:
        msg = 'Could not connect to RPC'
    except Web3Exception.error:
        msg = "web3 error"
    except ccxt.base.errors:
        msg = "CCXT error"
    except ccxt.NetworkError:
        msg = "Network error"
    except ccxt.ExchangeError:
        msg = "Exchange error"
    except Exception:
        msg = f"{e}"
    message = f"⚠️ {msg} {e}"
    logger.error(msg = f"{message}")
    await notify(message)

"""
🔚END OF COMMON FUNCTIONS
"""
#💾DB
async def database_setup():
    global ex_name
    global defaultenv
    global ex_test_mode
    global bot_db
    global cex_db
    global dex_db
    global bot_token
    global bot_channel_id
    global bot_service
    global bot_trading_switch
    global bot_hostname
    global bot_webhook_id
    global bot_webhook_token
    global bot_user
    global bot_pass
    global bot_api_id
    global bot_api_hash
    db_url=os.getenv("DB_URL")
    if db_url is None:
        logger.info(msg = "No remote DB variable, checking local file")
    else:
        outfile = os.path.join('./config', 'db.json')
        response = requests.get(db_url, stream=True)
        logger.debug(msg=f"{response}")
        #with open(outfile,'wb') as output:
        with open('./config/db.json','wb') as output:
            try:
                output.write(response.content)
                logger.debug(msg="remote DB copied")
            except Exception:
                logger.error(msg="error while copying the DB")

    db_path = './config/db.json'
    if os.path.exists(db_path):
        logger.info(msg="Existing DB found")
        try:
            db = TinyDB(db_path)
            q = Query()
            globalDB = db.table('global')
            defaultenv = globalDB.all()[0]['defaultenv']
            ex_name = globalDB.all()[0]['defaultex']
            ex_test_mode = globalDB.all()[0]['defaulttestmode']
            logger.info(msg=f"Env {defaultenv} ex {ex_name} testmode {ex_test_mode}")
            bot_db = db.table('bot')
            cex_db = db.table('cex')
            dex_db = db.table('dex')
            bot = bot_db.search(q.env == defaultenv)
            bot_trading_switch = True
            bot_service = bot[0]['service']
            bot_token = bot[0]['token']
            bot_channel_id = bot[0]['channel']
            bot_trading_switch = True
            if bot_service == 'discord':
                bot_webhook_id = bot[0]['webhook_id']
                bot_webhook_token = bot[0]['webhook_token']
            elif bot_service == 'matrix':
                bot_hostname = bot[0]['hostname']
                bot_user = bot[0]['user']
                bot_pass= bot[0]['pass']
            elif bot_service == 'telethon':
                bot_api_id = bot[0]['api_id']
                bot_api_hash = bot[0]['api_hash']
            if ((bot_service=='tgram') & (bot_token is None)): 
                logger.error("Failover process with sample DB")
                contingency_db_path = './config/sample_db.json'
                os.rename(contingency_db_path, db_path)
                try:
                    bot_token = os.getenv("TK") 
                    bot_channel_id = os.getenv("CHANNEL_ID")
                except Exception as e:
                    logger.error("no bot token")
                    sys.exit()
        except Exception as e:
            logger.warning(msg=f"error with db file {db_path}, verify json structure and content. error: {e}")


#🦾BOT ACTIONS
async def post_init():
    startup_message=f"Bot is online {TTversion}"
    logger.info(msg = f"{startup_message}")
    await notify(startup_message)

async def help_command():
    bot_ping = await verify_latency_ex()
    helpcommand = """
    🏦<code>/bal</code>
    🏛️<code>/cex kraken</code>
    🥞<code>/dex pancake</code>
    🦄<code>/dex uniswap_v2</code>
    📦<code>buy btc/usdt sl=1000 tp=20 q=1%</code>
        <code>buy cake</code>
    🦎 <code>/q BTCB</code>
           <code>/q WBTC</code>
           <code>/q btc/usdt</code>
    🔀 <code>/trading</code>
           <code>/testmode</code>"""
    if(bot_service=='discord'):
        helpcommand= helpcommand.replace("<code>", "`")
        helpcommand= helpcommand.replace("</code>", "`")
    bot_menu_help = f"{TTversion}\n{helpcommand}"
    return f"Environment: {defaultenv} Ping: {bot_ping}ms\nExchange: {ex_name} Sandbox: {ex_test_mode}\n{bot_menu_help}"

async def account_balance_command():
    balance =f"🏦 Balance\n"
    balance += await get_account_balance()
    return balance

async def account_position_command():
    logger.debug(msg="account_position_command")
    position = f"📊 Position\n"
    position += await get_account_position()
    return position

async def quote_command(symbol):
    asset_out_cg_quote = await fetch_gecko_quote(symbol)
    response=f"₿ {asset_out_cg_quote}\n"
    if (isinstance(ex,web3.main.Web3)):
        if(await search_contract(symbol) != None):
            asset_out_1inch_quote = await fetch_1inch_quote (symbol)
            response+=f"🦄{asset_out_1inch_quote} USD\n🖊️{chainId}: {await search_contract(symbol)}"
    else:
        price= ex.fetch_ticker(symbol.upper())['last']
        response+=f"🏛️ {price} USD"
    return response

async def exchange_switch_command(name):
    exchange_search = await search_exchange(name)
    if not exchange_search:
        return
    res = await load_exchange(exchange_search['name'])
    return f"{ex_name} is active"

async def trading_switch_command():
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    return f"Trading is {bot_trading_switch}"

async def testmode_switch_command():
    global ex_test_mode
    ex_test_mode = not ex_test_mode
    return f"Test mode is {ex_test_mode}"

async def restart_command():
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])


#🤖BOT
async def bot():
    global bot
    try:
#LOAD
        await verify_import_library()
        await database_setup()
        await load_exchange(ex_name)

        while True:
    #StartTheBot
            if bot_service == 'tgram':
                bot = Application.builder().token(bot_token).build()
                await post_init()
                bot.add_handler(MessageHandler(None, parse_message))
                async with bot:
                    await bot.initialize()
                    await bot.start()
                    await bot.updater.start_polling(drop_pending_updates=True)
            elif  bot_service =='discord':
                intents = discord.Intents.default()
                intents.message_content = True
                bot = discord.Bot(intents=intents)
                @bot.event
                async def on_ready():
                    await post_init()
                @bot.event
                async def on_message(message: discord.Message):
                    await parse_message(message,message.content)
                await bot.start(bot_token)
            elif bot_service== 'matrix':
                config = botlib.Config()
                config.emoji_verify = True
                config.ignore_unverified_devices = True
                config.store_path ='./config/matrix/'
                creds = botlib.Creds(bot_hostname, bot_user, bot_pass)
                bot = botlib.Bot(creds,config)
                @bot.listener.on_startup
                async def room_joined(room):
                    await post_init()
                @bot.listener.on_message_event
                async def neo(room, message):    
                    await parse_message(bot,message.body)
                await bot.api.login()
                bot.api.async_client.callbacks = botlib.Callbacks(bot.api.async_client, bot)
                await bot.api.async_client.callbacks.setup_callbacks()
                for action in bot.listener._startup_registry:
                    for room_id in bot.api.async_client.rooms:
                        await action(room_id)
                await bot.api.async_client.sync_forever(timeout=3000, full_state=True)
            elif bot_service == 'telethon':
                bot = await TelegramClient(None, bot_api_id, bot_api_hash).start(bot_token=bot_token)
                await post_init()
                @bot.on(events.NewMessage())
                async def telethon(event):
                    await parse_message(bot,event.message.message)
                await bot.run_until_disconnected()

    except Exception as e:
        logger.error(msg=f"Bot failed to start: {str(e)}")

#⛓️API
app = FastAPI(title="TALKYTRADER",)

@app.on_event("startup")
def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(bot())
    logger.info(msg="Webserver started")

@app.on_event('shutdown')
async def shutdown_event():
    logger.info('Webserver shutting down...')

@app.get("/")
def root():
    return {f"Bot is online {TTversion}"}

@app.get("/health")
def health_check():
    logger.info(msg="Healthcheck_Ping")
    return {f"Bot is online {TTversion}"}

@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request):
    payload = await request.body()
    logger.info(msg=f"webhook event {payload}")

@app.post("/notify", status_code=http.HTTPStatus.ACCEPTED)
async def notifybot(request: Request):
    data_received = await request.body()
    await notify(data_received)
    logger.info(msg=f"notifybot event {data_received}")

#🙊TALKYTRADER
if __name__ == '__main__':
    HOST=os.getenv("HOST", "0.0.0.0")
    PORT=os.getenv("PORT", "8080")
    uvicorn.run(app, host=HOST, port=PORT)


