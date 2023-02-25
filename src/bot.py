##=============== VERSION =============

TTversion="🪙📞🗿 TT Beta 1.2.78"

##=============== import  =============
##log
import logging
import sys
import traceback
##env
import os
from dotenv import load_dotenv
import json, requests
import asyncio
#telegram
#import telegram
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
#import telethon
from telethon import TelegramClient, events
#matrix
import simplematrixbotlib as botlib
#discord
import discord
from discord.ext import commands
#notification
import apprise
from apprise import NotifyFormat
#db
from tinydb import TinyDB, Query, where
#CEX
import ccxt
#DEX
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from ens import ENS
from datetime import datetime
#API
from fastapi import FastAPI, Header, HTTPException, Request
import uvicorn
import http
#Utils
from pycoingecko import CoinGeckoAPI
from ping3 import ping

#🔧CONFIG
load_dotenv()

#🧐LOGGING
LOGLEVEL=os.getenv("LOGLEVEL", "INFO")
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info(msg=f"LOGLEVEL {LOGLEVEL}")

#🔗API
gecko_api = CoinGeckoAPI() # llama_api = f"https://api.llama.fi/" maybe as backup
dex_1inch_api = "https://api.1inch.exchange/v5.0"

#🔁UTILS
async def verify_import_library():
    logger.info(msg=f"{TTversion}")

async def parse_message(self,msg='123'):
    logger.debug(msg=f"parse_message SELF {self}")
    logger.debug(msg=f"parse_message: {msg}")
    if(bot_service=='tgram'):
        msg=self.effective_message.text
    wordlist = msg.split(" ")
    wordlistsize = len(wordlist)
    logger.debug(msg=f"parse_message wordlist {wordlist} len {wordlistsize}")
    response = ""
    #🦾BOT FILTERS
    filter_lst_ignore = ['⚠️','error','Environment','Balance','Bot']
    filter_lst_order = ['BUY', 'SELL', 'buy','sell']
    filter_lst_help = ['/echo','/help']
    filter_lst_bal = ['/bal']
    filter_lst_pos = ['/pos']
    filter_lst_quote = ['/q']
    filter_lst_trading = ['/trading']
    filter_lst_test = ['/testmode']
    filter_lst_restart = ['/restart']
    filter_lst_switch = ['/cex', '/dex', '/cext','/dext']
    try:
        if [ele for ele in filter_lst_ignore if(ele in wordlist)]:
            return
        elif [ele for ele in filter_lst_help if(ele in wordlist)]:
            response = await help_command()
        elif [ele for ele in filter_lst_order if(ele in wordlist)]:
            if wordlistsize > 1:
                direction = wordlist[0].upper()
                symbol = wordlist[1]
                stoploss = 100
                takeprofit = 100
                quantity = 10
                if wordlistsize > 2:
                    stoploss = wordlist[2][3:]
                    takeprofit = wordlist[3][3:]
                    quantity = wordlist[4][2:-1]
                order=[direction,symbol,stoploss,takeprofit,quantity]
                logger.info(msg=f"parse_message Order: {order}")
                #return order
                if order:
                    res = await execute_order(order[0],order[1],order[2],order[3],order[4])
                    if res is None:
                        return
                    response = f"{res}"
                    logger.debug(msg=f"parse_message order response: {response}")
        elif [ele for ele in filter_lst_switch if(ele in wordlist)]:
            if wordlistsize > 0:
                response = await exchange_switch_command(wordlist[1])
            else:
                return
        elif [ele for ele in filter_lst_bal if(ele in wordlist)]:
            response= await account_balance_command(self)
        elif [ele for ele in filter_lst_pos if(ele in wordlist)]:
            response= await  account_position_command(self)
        elif [ele for ele in filter_lst_trading if(ele in wordlist)]:
            response = await  trading_switch_command(self)
        elif [ele for ele in filter_lst_test if(ele in wordlist)]:
            response = await testmode_switch_command(self)
        elif [ele for ele in filter_lst_restart if(ele in wordlist)]:
            response = await  restart_command(self)
        elif [ele for ele in filter_lst_quote if(ele in wordlist)]:
            if wordlistsize > 0:
                response = await quote_command(wordlist[1])
        else:
            logger.debug(msg=f"Parsing skipped {wordlist}")
            return
        if (response != ""):
            await notify(response)
            #await send_msg(self,response)
    except Exception as e:
        logger.warning(msg=f"Parsing exception {e}")
        return

async def retrieve_url_json(url,params=None):
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url,params =params,headers=headers)
    return response.json()

async def verify_latency_ex():
    try:
        return (
            round(ping(ex_node_provider, unit='ms'), 3)
            if isinstance(ex, web3.main.Web3)
            else round(ping("1.1.1.1", unit='ms'), 3)
        )
    except Exception as e:
        await handle_exception(e)

#💬MESSAGING
# async def send_msg (self="bot", msg="echo"):
#     logger.debug(msg=f"💬MESSAGING START self {self} msg {msg}")
#     try:
#         if(bot_service=='tgram'):
#             #await self.send_message(msg, parse_mode=constants.ParseMode.HTML)
#             await self.effective_chat.send_message(msg, parse_mode=constants.ParseMode.HTML)
#             #await self.chat.send_message(f"{msg}", parse_mode=constants.ParseMode.HTML)
#             #await self.bot.send_message(bot_channel_id, msg, parse_mode=constants.ParseMode.HTML)
#             return 
#         elif(bot_service=='discord'):
#             embed = discord.Embed(description=msg)
#             channel = bot.get_channel(int(bot_channel_id))
#             await channel.send(embed=embed)
#         elif(bot_service=='matrix'):
#             # await bot.api.send_text_message(bot_channel_id, msg)
#             await bot.api.send_markdown_message(bot_channel_id, msg)
#             return
#         elif(bot_service=='telethon'):
#             await self.send_message(int(bot_channel_id),msg,parse_mode='html')
#             return
#     except Exception as e:
#         logger.warning(msg=f"{msg} {e}")
#         await handle_exception(e)

async def notify(msg):
    if msg == "":
        return
    logger.debug(msg=f"NOTIFICATION START {msg}")
    apobj = apprise.Apprise()
    if bot_service in ['tgram', 'telethon']:
        apobj.add(f'tgram://{str(bot_token)}/{str(bot_channel_id)}')
    elif (bot_service =='discord'):
        apobj.add(f'{bot_service}://{str(bot_webhook_id)}/{str(bot_webhook_token)}')
    elif (bot_service =='matrix'):
        apobj.add(
            f"matrixs:// {bot_user}:{bot_pass}@{bot_hostname[8:]}:443/{str(bot_channel_id)}"
        )
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
    exchange_info = await search_gecko_exchange(exchangeid)
    logger.debug(msg=f"exchange_info {exchange_info}")
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
        ex = Web3(Web3.HTTPProvider(f'https://{ex_node_provider}'))
        ex.middleware_onion.inject(geth_poa_middleware, layer=0)
        #ns = ENS.from_web3(ex)
        #await resolve_ens_dex(router)
        router_instanceabi= await fetch_abi_dex(router) #Router ABI
        logger.info(msg=f"router_instanceabi {router_instanceabi}")
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
        defaultType =  ex_result['defaultType'],
        chainId= 0
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
            # ex_info = await search_gecko_exchange(ex_name)
            # logger.info(msg=f"gecko {ex_info}")
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
            if (await get_account_balance()=="No Balance"): 
                msg = "Check your Balance"
                await handle_exception(msg)
                return
            totalusdtbal = ex.fetchBalance()['USDT']['free']
            amountpercent=((totalusdtbal)*(float(quantity)/100))/float(m_price) # % of bal
            res = ex.create_order(symbol, price_type, direction, amountpercent)
            response = f"⬇️ {symbol}" if (direction=="SELL") else f"⬆️ {symbol}"
            response+= f"\n➕ Size: {res['amount']}\n⚫️ Entry: {res['price']}\nℹ️ {res['id']}\n🗓️ {res['datetime']}"

        else:
            asset_out_symbol = basesymbol if direction=="BUY" else symbol
            asset_in_symbol = symbol if direction=="BUY" else basesymbol
            logger.debug(msg=f"asset_out_symbol {asset_out_symbol} asset_in_symbol {asset_in_symbol}")
            response = f"⬆️ {asset_in_symbol}" if direction=="BUY" else f"⬇️ {asset_out_symbol}"
            asset_out_address= await search_gecko_contract(asset_out_symbol)
            asset_out_abi= await fetch_abi_dex(asset_out_address)
            asset_out_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            asset_in_address= await search_gecko_contract(asset_in_symbol)
            order_path_dex=[asset_out_address, asset_in_address]
            asset_out_decimals=asset_out_contract.functions.decimals().call()
            asset_out_balance=await fetch_user_token_balance(asset_out_symbol)
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
            if dex_version == 'uni_v2':
                await approve_asset_router(asset_out_address)
                transaction_getoutput_amount  = router_instance.functions.getOutputAmount(transaction_amount, order_path_dex).call()
                transaction_minimum_amount = int(transaction_getoutput_amount[1])
                swap_TX = router_instance.functions.swapExactTokensForTokens(transaction_amount,transaction_minimum_amount,order_path_dex,walletaddress,deadline)
                tx_token = await sign_transaction_dex(swap_TX)

            elif dex_version == "1inch_LimitOrder_v2":
                return
            elif dex_version == "1inch_v5.0":
                await approve_asset_router(asset_out_address)
                swap_url = f"{dex_1inch_api}/{chainId}/swap?fromTokenAddress={asset_out_address}&toTokenAddress={asset_in_address}&amount={transaction_amount}&fromAddress={walletaddress}&slippage={slippage}"
                swap_TX = await retrieve_url_json(swap_url)
                tx_token= await sign_transaction_dex(swap_TX)

            elif dex_version == "uni_v3":
                await approve_asset_router(asset_out_address)
                sqrtPriceLimitX96 = 0
                fee = 3000
                transaction_minimum_amount = self.quoter.functions.quoteExactInputSingle(asset_out_address, asset_in_address, fee, transaction_amount, sqrtPriceLimitX96).call()
                swap_TX = router_instance.functions.exactInputSingle(asset_in_address,asset_out_address,fee,walletaddress,deadline,transaction_amount,transaction_minimum_amount,sqrtPriceLimitX96)
                tx_token = await sign_transaction_dex(swap_TX)

            txHash = str(ex.to_hex(tx_token))
            txResult = await fectch_transaction_dex(txHash)
            txHashDetail=ex.eth.wait_for_transaction_receipt(txHash, timeout=120, poll_latency=0.1)
            if(txResult == "1"):
                response+= f"\n➕ Size: {round(ex.from_wei(transaction_amount, 'ether'),5)}\n⚫️ Entry: {await fetch_gecko_asset_price(asset_in_address)}USD \nℹ️ {txHash}\n⛽️ {txHashDetail['gasUsed']}\n🗓️ {datetime.now()}"
                logger.info(msg=f"{response}")

        return response

    except Exception as e:
        logger.debug(msg=f"order debugger {e}")
        await handle_exception(e)
        return

#🦄DEX
async def resolve_ens_dex(addr):
    try:
        domain = ns.name(addr)
        logger.debug(msg=f"ENS {domain}")
        return
    except Exception as e:
        await handle_exception(e)

async def approve_asset_router(asset_out_address):
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
        await handle_exception(e)

async def sign_transaction_dex(contract_tx):
    try:
        if dex_version in ['uni_v2', "uni_v3"]:
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
        elif dex_version == "1inch_v5":
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
        abi = resp["result"]
        #logger.debug(msg=f"abi {abi}")
        return abi if (abi!="") else None
    except Exception as e:
        await handle_exception(e)

async def fectch_transaction_dex(txHash):
    checkTransactionSuccessURL = f"{abiurl}?module=transaction&action=gettxreceiptstatus&txhash={txHash}&apikey={abiurltoken}"
    checkTransactionRequest =  await retrieve_url_json(checkTransactionSuccessURL)
    return checkTransactionRequest['status']

async def fetch_1inch_quote(token):
    asset_in_address = await search_gecko_contract(token)
    asset_out_address = await search_gecko_contract('USDC')
    try:
        asset_out_amount=1000000000000
        quote_url = f"{dex_1inch_api}/{chainId}/quote?fromTokenAddress={asset_in_address}&toTokenAddress={asset_out_address}&amount={asset_out_amount}"
        quote = retrieve_url_json(quote_url)
        logger.debug(msg=f"quote {quote}")
        return quote['toTokenAmount']
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
        logger.debug(msg=f"token_contract {token_contract}")
        token_balance=asset_out_contract.functions.balanceOf(walletaddress).call()
        return 0 if token_balance <=0 or token_balance is None else token_balance
    except Exception:
        return 0

async def fetch_account_dex(addr):
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
    return int(d['result']) / self.zeroes

async def estimate_gas(tx):
    estimate_gas_cost = int(ex.to_wei(ex.eth.estimate_gas(tx) * 1.2),'wei')
    
# async def verify_gas():
#     current_gas_price = int(ex.to_wei(ex.eth.gas_price,'wei'))
#     config_gas_price_dex = int(ex.to_wei(gasPrice,'gwei'))
#     if (current_gas_price_dex>=config_gas_price_dex):
#         logger.warning(msg=f"{current_gas_price_dex} {config_gas_price_dex} ")
#     else:
#         logger.info(msg=f"gas setup{config_gas_price_dex} aligned with current gas price {current_gas_price_dex}")

async def search_test_contract(symbol):
    try:
        tokenlist = 'https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json'
        token_list = await retrieve_url_json(tokenlist)
        token_list = json.loads(text)['tokens']
        logger.info(msg=f"token_list {token_list}")
        symbolcontract = [token for token in token_list if (token['symbol'] == symbol and token['chainId']==chainId)]
        logger.info(msg=f"📝 contract  {symbolcontract}")
        if symbolcontract:
            return symbolcontract[0]['address']
    except Exception as e:
        logger.error(msg=f"search_test_contract error {token}")
        await HandleExceptions(e)
        return

#🦎GECKO
async def search_gecko(token):
    try:
        symbol_info = gecko_api.search(query=token)
        logger.debug(msg=f"🦎 Search {symbol_info}")
        for i in symbol_info['coins']:
            results_search_coin = i['symbol']
            if (results_search_coin==token.upper()):
                api_symbol = i['api_symbol']
                coin_info =gecko_api.get_coin_by_id(api_symbol)
                logger.debug(msg=f"coin_info {coin_info}")
                return coin_info
    except Exception:
        return

async def search_gecko_detailed(token):
    try:
        coin_info = await search_gecko(token)
        coin_symbol= coin_info['symbol']
        coin_platform = coin_info['asset_platform_id']
        coin_image = coin_info['image']['small']
        coin_link = coin_info['links']['homepage'][0]
        coin_price = coin_info['market_data']['current_price']['usd']
        return f'Symbol {coin_symbol}\nPlatform {coin_platform}\nPrice: {coin_price} USD\nmore info {coin_link} {coin_image}'
    except Exception:
        return

async def search_gecko_contract(token):
    try:
        if (ex_test_mode=='True'):
            logger.info(msg="📝 test contract search")
            coin_contract = await search_test_contract(token)
            logger.info(msg=f"📝 contract {token} {coin_contract}")
        else:
            coin_info = await search_gecko(token)
            coin_contract = coin_info['platforms'][f'{await search_gecko_platform()}']
            logger.info(msg=f"🦎 contract {token} {coin_contract}")
        return ex.to_checksum_address(coin_contract)
    except Exception:
        return

async def search_gecko_platform():
    try:
        assetplatform = gecko_api.get_asset_platforms()
        for i in assetplatform:
            results_search_chain = i['chain_identifier']
            if (results_search_chain == int(chainId)):
                return i['id']
    except Exception:
        return

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
        asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{await search_gecko_platform()}',contract_address=asset_in_address)
        logger.debug(msg=f"fetch_tokeninfo{fetch_tokeninfo}")
        return fetch_tokeninfo['market_data']['current_price']['usd']
    except Exception as e:
        print(f"An error occurred while retrieving address {e}")

async def fetch_gecko_quote(token):
    try:
        asset_in_address = ex.to_checksum_address(await search_gecko_contract(token))
        fetch_tokeninfo = gecko_api.get_coin_info_from_contract_address_by_id(id=f'{await search_gecko_platform()}',contract_address=asset_in_address)
        logger.debug(msg=f"fetch_tokeninfo{fetch_tokeninfo}")
        asset_out_cg_quote = fetch_tokeninfo['market_data']['current_price']['usd']
        asset_out_cg_name = fetch_tokeninfo['name']
        return f"{asset_out_cg_name}\n🦎{asset_out_cg_quote} USD"
    except Exception:
        return

#🔒PRIVATE
async def get_account_balance():
    try:
        logger.debug(msg="get_account_balance")
        msg = ""
        if not isinstance(ex,web3.main.Web3):
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            sbal = "".join(f"{iterator}: {value} \n" for iterator, value in bal.items())
            if not sbal:
                sbal = "No Balance"
            msg += f"{sbal}"
        else:
            logger.debug(msg="WEB3 BALANCE ECHO")
            bal = ex.eth.get_balance(walletaddress)
            logger.debug(msg=f"message {bal}")
            bal = round(ex.from_wei(bal,'ether'),5)
            basesymbol_bal = round(ex.from_wei(await fetch_user_token_balance(basesymbol),'ether'),5)
            msg += f"💲{bal} \n💵{basesymbol_bal} {basesymbol}"
            logger.debug(msg=f"message {msg}")
        return msg
    except Exception as e:
        return

async def get_account_position():
    try:
        logger.debug(msg="get_account_position")
        if not isinstance(ex,web3.main.Web3):
            positions = ex.fetch_positions()
            logger.debug(f"positions {positions}")
            open_positions = [p for p in positions if p['type'] == 'open']
            logger.debug(f"open_positions {open_positions}")
            msg = f"open_positions {open_positions}"
        else:
            # asset_position_address= await search_gecko_contract(asset_out_symbol)
            # asset_position_abi= await fetch_abi_dex(asset_out_address)
            # asset_position_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            # open_positions = asset_position_contract.functions.getOpenPositions(walletaddress).call()
            pos = "ECHO"
            logger.debug(msg=f"pos {pos}")
            msg = f"{pos}"
        logger.debug(f"msg {msg}")
        return msg
    except Exception:
        logger.debug("get_account_position exception")

async def get_wallet_auth():
    try:
        return
    except Exception as e:
        return

#======= error handling
async def handle_exception(e) -> None:
    try:
        msg = ""
        logger.error(msg=f"error: {e}")
    except KeyError:
        msg = "DB content error"
        sys.exit()
    except IndexError:
        msg = "Parsing error"
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
        logger.info(msg="No remote DB variable, checking local file")
    else:
        outfile = os.path.join('./config', 'db.json')
        response = requests.get(db_url, stream=True)
        logger.debug(msg=f"{response}")
        #with open(outfile,'wb') as output:
        with open('./config/db.json','wb') as output:
            output.write(response.content)
            logger.debug(msg="remote DB copied")

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
            logger.debug(msg=f"{bot}")
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
            if ((bot_service=='tgram') & (bot_token == "")): 
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
async def post_init(self='bot'):
    logger.info(msg = f"self {self}")
    startup_message=f"Bot is online {TTversion}"
    logger.info(msg = f"{startup_message}")
    await notify(startup_message)

async def help_command() -> None:
    bot_ping = await verify_latency_ex()
    helpcommand = """
    🏦 <code>/bal</code>
    🏛️ <code>/cex kraken</code>
    🥞 <code>/dex pancake</code>
    🦄 <code>/dex uniswap_v2</code>
    📦 <code>buy btc/usdt sl=1000 tp=20 q=1%</code>
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

async def account_balance_command(self='bot') -> None:
    balance =f"🏦 Balance\n"
    balance += await get_account_balance()
    return balance

async def account_position_command(self='bot') -> None:
    position = f"📊 Position\n"
    position += await get_account_position()
    return position

async def quote_command(symbol) -> None:
    asset_out_cg_quote = await fetch_gecko_quote(symbol)
    response=f"₿ {asset_out_cg_quote}\n"
    if (isinstance(ex,web3.main.Web3)):
        if(await search_gecko_contract(symbol) != None):
            asset_out_1inch_quote = await fetch_1inch_quote (symbol)
            response+=f"🦄{asset_out_1inch_quote} USD\n🖊️{chainId}: {await search_gecko_contract(symbol)}"
            #response+=f"/n{await search_gecko_detailed(symbol)}"
    else:
        price= ex.fetch_ticker(symbol.upper())['last']
        response+=f"🏛️ {price} USD"
    return response

async def exchange_switch_command(name):
    exchange_search = await search_exchange(name)
    logger.debug(msg=f"exchange_search {exchange_search}")
    res = await load_exchange(exchange_search['name'])
    logger.debug(msg=f"res {res}")
    return f"{ex_name} is active"

async def trading_switch_command(self='bot') -> None:
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    return f"Trading is {bot_trading_switch}"

async def testmode_switch_command(self='bot') -> None:
    global ex_test_mode
    ex_test_mode = not ex_test_mode
    return f"Test mode is {ex_test_mode}"

async def restart_command(self='bot') -> None:
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e = f"{tb_trim}"
    await handle_exception(e)

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
            if(bot_service=='tgram'):
                bot = Application.builder().token(bot_token).build()
                await post_init(bot)
                bot.add_handler(MessageHandler(None, parse_message))
                bot.add_error_handler(error_handler)
                #bot.run_polling(drop_pending_updates=True)
                async with bot:
                    await bot.initialize()
                    await bot.start()
                    await bot.updater.start_polling(drop_pending_updates=True)
            elif(bot_service=='discord'):
                intents = discord.Intents.default()
                intents.message_content = True
                bot = discord.Bot(intents=intents)
                @bot.event
                async def on_ready():
                    await post_init(bot)
                @bot.event
                async def on_message(message: discord.Message):
                    await parse_message(message,message.content)
                await bot.start(bot_token)
            elif(bot_service=='matrix'):
                config = botlib.Config()
                config.emoji_verify = True
                config.ignore_unverified_devices = True
                config.store_path ='./config/matrix/'
                creds = botlib.Creds(bot_hostname, bot_user, bot_pass)
                bot = botlib.Bot(creds,config)
                @bot.listener.on_startup
                async def room_joined(room):
                    await post_init(bot)
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
            elif(bot_service=='telethon'):
                bot = await TelegramClient(None, bot_api_id, bot_api_hash).start(bot_token=bot_token)
                await post_init(bot)
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
    uvicorn.run(app, host='0.0.0.0', port=8080)


