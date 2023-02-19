##=============== VERSION =============
TTversion="🪙TT Beta 1.2.62"
##=============== import  =============
##log
import logging
import sys
import traceback
from ping3 import ping
##env
import os
from dotenv import load_dotenv
import json, requests
import asyncio
import nest_asyncio
from aiohttp import web

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
from pycoingecko import CoinGeckoAPI


#🔧CONFIG
load_dotenv()
nest_asyncio.apply()
#🧐LOGGING
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

#🔗API
gecko_api = CoinGeckoAPI()
llama_api = f"https://api.llama.fi/"
dex_1inch_api = f"https://api.1inch.exchange/v5.0"

#🔁UTILS
async def verify_import_library():
    logger.info(msg=f"{TTversion}")

async def parse_message (self,msg='123'):
    logger.debug(msg=f"parse_message SELF {self}")
    logger.debug(msg=f"parse_message: {msg}")
    if(bot_service=='tgram'):
        msg=self.effective_message.text
    wordlist = msg.split(" ")
    logger.debug(msg=f"parse_message wordlist {wordlist}")
    response = ""
    #🦾BOT FILTERS
    filter_lst_ignore = ['⚠️','error', 'Environment','Balance']
    filter_lst_order = ['BUY', 'SELL', 'buy','sell']
    filter_lst_help = ['/echo','/help']
    filter_lst_bal = ['/bal']
    filter_lst_pos = ['/pos']
    filter_lst_quote = ['/q'] 
    filter_lst_trading = ['/trading']
    filter_lst_test = ['/testmode']
    filter_lst_restart = ['/restart']
    filter_lst_switch = ['/cex', '/dex']
    logger.debug(msg=f"parse_message wordlist len {len(wordlist)}")
    try:
        if [ele for ele in filter_lst_ignore if(ele in wordlist)]:
            return
        elif [ele for ele in filter_lst_help if(ele in wordlist)]:
            logger.info(msg=f"filter_lst_help: {wordlist}")
            response = await help_command()
        elif [ele for ele in filter_lst_order if(ele in wordlist)]:
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
                    logger.info(msg=f"parse_message Order: {order}")
                    #return order
                    if (order):
                        res = await execute_order(order[0],order[1],order[2],order[3],order[4])
                        if (res != None):
                            response = f"{res}"
                            logger.info(msg=f"parse_message order response: {response}")
                        else:
                            return
        elif [ele for ele in filter_lst_switch if(ele in wordlist)]:
            if len(wordlist[1]) > 0:
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
            if len(wordlist[1]) > 0:
                response = await quote_command(wordlist[1])
        else:
            logger.info(msg=f"Parsing skipped {wordlist}")
            return
        if (response != ""):
            await send_msg(self,response)
    except Exception as e:
        logger.info(msg=f"Parsing exception {e}")
        return

async def retrieve_url_json(url,params=None):
    headers = { "User-Agent": "Mozilla/5.0" }
    response = requests.get(url,params =params,headers=headers)
    response_json = response.json()
    return response_json

async def verify_latency_ex():
    try:
        logger.debug(msg=f"LATENCY CHECK")
        ping_url="1.1.1.1"
        response = round(ping(ping_url, unit='ms'),3)
        logger.debug(msg=f"LATENCY {response}")
        return response
        # if not isinstance(ex,web3.main.Web3):
        #     symbol = 'BTC/USDT'
        #     results = []
        #     num_iterations = 5
        #     for i in range(0, num_iterations):
        #         started = ex.milliseconds()
        #         orderbook = ex.fetch_order_book(symbol)
        #         ended = ex.milliseconds()
        #         elapsed = ended - started
        #         results.append(elapsed)
        #         rtt = int(sum(results) / len(results))
        #         response = rtt
        # elif (isinstance(ex,web3.main.Web3)):
        #     response = round(ping(ex_node_provider, unit='ms'),3)
        #     return response
    except Exception as e:
        await handle_exception(e)

#💬MESSAGING
async def send_msg (self="bot", msg="echo"):
    logger.debug(msg=f"💬MESSAGING START")
    logger.debug(msg=f"self {self} msg {msg} ")
    try:
        if(bot_service=='tgram'):
            #await self.send_message(msg, parse_mode=constants.ParseMode.HTML)
            await self.effective_chat.send_message(msg, parse_mode=constants.ParseMode.HTML)
            #await self.chat.send_message(f"{msg}", parse_mode=constants.ParseMode.HTML)
            #await self.bot.send_message(bot_channel_id, msg, parse_mode=constants.ParseMode.HTML)
            return 
        elif(bot_service=='discord'):
            embed = discord.Embed(description=msg)
            channel = bot.get_channel(int(bot_channel_id))
            await channel.send(embed=embed)
        elif(bot_service=='matrix'):
            # await bot.api.send_text_message(bot_channel_id, msg)
            await bot.api.send_markdown_message(bot_channel_id, msg)
            return
        elif(bot_service=='telethon'):
            await self.send_message(int(bot_channel_id),msg,parse_mode='html')
            return
    except Exception as e:
        logger.debug(msg=f"MESSAGING EXCEPTION")
        await handle_exception(e)

async def notify(msg):
    if (msg!=""):
        logger.debug(msg=f"NOTIFICATION START {msg}")
        apobj = apprise.Apprise()
        if (bot_service =='tgram') or (bot_service =='telethon'):
            apobj.add(f'tgram://' + str(bot_token) + "/" + str(bot_channel_id))
        elif (bot_service =='discord'):
            apobj.add(f'{bot_service}://' + str(bot_webhook_id) + "/" + str(bot_webhook_token))
        elif (bot_service =='matrix'):
            apobj.add(f"matrixs:// "+bot_user+":"+ bot_pass +"@" +bot_hostname[8:] +":80/" + bot_channel_id)
        try:
            apobj.notify(body=msg)
        except Exception as e:
            logger.error(msg=f"{msg} not sent due to error: {e}")

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
                logger.info(msg=f"sandbox setup")
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
                logger.debug(msg=f"m_price: {m_price}")
                totalusdtbal = ex.fetchBalance()['USDT']['free']
                logger.debug(msg=f"totalusdtbal: {totalusdtbal}")
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
        logger.debug(msg=f"order debugger {e}")
        await handle_exception(e)
        return

#🦄DEX
async def resolve_ens_dex(addr):
    try:
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
        abi = resp["result"]
        #logger.debug(msg=f"abi {abi}")
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
        quote = retrieve_url_json(quote_url)
        #logger.debug(msg=f"quote {quote}")
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
        logger.debug(msg=f"token_contract {token_contract}")
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

async def search_test_contract(symbol):
    try:
        tokenlist = 'https://raw.githubusercontent.com/mraniki/tokenlist/main/TT.json'
        token_list = await retrieve_url_json(tokenlist)
        token_list = json.loads(text)['tokens']
        logger.info(msg=f"token_list {token_list}")
        symbolcontract = [token for token in token_list if (token['symbol'] == symbol and token['chainId']==chainId)]
        logger.info(msg=f"📝 contract  {symbolcontract}")
        if len(symbolcontract) > 0:
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
        response = f'Symbol {coin_symbol}\nPlatform {coin_platform}\nPrice: {coin_price} USD\nmore info {coin_link} {coin_image}'
        return response
    except Exception:
        return

async def search_gecko_contract(token):
    try:
        if (ex_test_mode=='True'):
            logger.info(msg=f"📝 test contract search")
            coin_contract = await search_test_contract(token)
            logger.info(msg=f"📝 contract {token} {coin_contract}")
            return ex.to_checksum_address(coin_contract)
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
        logger.debug(msg=f"get_account_balance")
        msg = ""
        if not isinstance(ex,web3.main.Web3):
            bal = ex.fetch_free_balance()
            bal = {k: v for k, v in bal.items() if v is not None and v>0}
            sbal = ""
            for iterator in bal:
                sbal += (f"{iterator}: {bal[iterator]} \n")
            if(sbal == ""):
                sbal = "No Balance"
            msg += f"{sbal}"       
        elif (isinstance(ex,web3.main.Web3)):
            logger.debug(msg=f"WEB3 BALANCE ECHO")
            bal = ex.eth.get_balance(walletaddress)
            logger.debug(msg=f"message {bal}")
            bal = round(ex.from_wei(bal,'ether'),5)
            basesymbol_bal = round(ex.from_wei(await fetch_user_token_balance(basesymbol),'ether'),5)
            msg += f"💲{bal} \n💵{basesymbol_bal} {basesymbol}"
            logger.debug(msg=f"message {msg}")
        else:
            msg += 0
        return msg
    except Exception as e:
        return

async def get_account_position():
    try:
        logger.debug(msg=f"get_account_position")
        if not isinstance(ex,web3.main.Web3):
            positions = ex.fetch_positions()
            logger.debug(f"positions {positions}")
            open_positions = [p for p in positions if p['type'] == 'open']
            logger.debug(f"open_positions {open_positions}")
            msg = f"open_positions {open_positions}"
        elif (isinstance(ex,web3.main.Web3)):
            # asset_position_address= await search_gecko_contract(asset_out_symbol)
            # asset_position_abi= await fetch_abi_dex(asset_out_address)
            # asset_position_contract = ex.eth.contract(address=asset_out_address, abi=asset_out_abi)
            # open_positions = asset_position_contract.functions.getOpenPositions(walletaddress).call()
            pos = "ECHO"
            logger.debug(msg=f"pos {pos}")
            msg = f"{pos}"
        else:
            msg = 0
        logger.debug(f"msg {msg}")
        return msg
    except Exception:
        logger.debug(f"get_account_position exception")

async def get_wallet_auth():
    try:
        return
    except Exception as e:
        return

#======= error handling
async def handle_exception(e) -> None:
    try:
        msg = f"!error:"
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


#🦾BOT ACTIONS
async def appserver():
    global app
    try:
        logger.info(msg = f"Starting appserver")
        app = web.Application()
        app.add_routes([web.get('/', health_check)])
        web.run_app(app)
        logger.info(msg = f"exiting appserver setup")
    except Exception as e:    
        logger.warning(msg=f"HealthCheck server error {e}")

async def health_check():
    logger.info(msg = f"Healthcheck_Ping")
    headers = { "User-Agent": "Mozilla/5.0" }
    return web.Response(body=f"Bot is online {TTversion}",status=200,headers=headers)

async def post_init(self='bot'):
    await appserver()
    logger.info(msg = f"self {self}")
    startup_message=f"Bot is online {TTversion}"
    logger.info(msg = f"{startup_message}")
    if(bot_service=='discord'or bot_service=='telethon' or bot_service=='matrix'):
        await send_msg(self,startup_message)
    if(bot_service=='tgram'):
        await self.bot.send_message(bot_channel_id, startup_message, parse_mode=constants.ParseMode.HTML)

async def help_command(self='bot') -> None:
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
        helpcommand= msg.replace("<code>", "`")
        helpcommand= msg.replace("</code>", "`")
    bot_menu_help = f"{TTversion}\n{helpcommand}"
    response= f"Environment: {defaultenv} Ping: {bot_ping}ms\nExchange: {ex_name} Sandbox: {ex_test_mode}\n{bot_menu_help}"
    return response

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
    elif not (isinstance(ex,web3.main.Web3)):
        price= ex.fetch_ticker(symbol.upper())['last']
        response+=f"🏛️ {price} USD"
    return response

async def exchange_switch_command(name):
    exchange_search = await search_exchange(name)
    logger.debug(msg=f"exchange_search {exchange_search}")
    res = await load_exchange(exchange_search['name'])
    logger.debug(msg=f"res {res}")
    response = f"{ex_name} is active"
    return response

async def trading_switch_command(self='bot') -> None:
    global bot_trading_switch
    bot_trading_switch = not bot_trading_switch
    response=f"Trading is {bot_trading_switch}"
    return response

async def testmode_switch_command(self='bot') -> None:
    global ex_test_mode
    ex_test_mode = not ex_test_mode
    response = f"Test mode is {ex_test_mode}"
    return response

async def restart_command(self='bot') -> None:
    os.execl(sys.executable, os.path.abspath(__file__), sys.argv[0])

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    tb_trim = tb_string[:1000]
    e = f"{tb_trim}"
    await handle_exception(e)
    logger.DEBUG(msg="HANDLER")

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
    if db_url == None:
        logger.info(msg = f"No remote DB variable, checking local file")
    else:
        outfile = os.path.join('./config', 'db.json')
        response = requests.get(db_url, stream=True)
        logger.debug(msg=f"{response}")
        with open(outfile,'wb') as output:
          output.write(response.content)
          logger.debug(msg = f"remote DB copied")
          
    db_path = './config/db.json'
    if os.path.exists(db_path):
        logger.info(msg=f"Existing DB found")
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
            if (bot_service=='discord'):
                bot_webhook_id = bot[0]['webhook_id']
                bot_webhook_token = bot[0]['webhook_token']
            if (bot_service=='matrix'):
                bot_hostname = bot[0]['hostname']
                bot_user = bot[0]['user']
                bot_pass= bot[0]['pass']
            if (bot_service=='telethon'):
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
            logger.error(msg=f"error with db file {db_path}, verify json structure and content. error: {e}")

#🤖BOT
async def main():
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
                bot.run_polling(drop_pending_updates=True)
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
                bot.run(bot_token)
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
                    match = botlib.MessageMatch(room, message, bot)
                    if match.is_not_from_this_bot():    
                        await parse_message(bot,message.body)
                bot.run()
            elif(bot_service=='telethon'):
                bot = await TelegramClient(None, bot_api_id, bot_api_hash).start(bot_token=bot_token)
                await post_init(bot)
                @bot.on(events.NewMessage())
                async def telethon(event):
                    await parse_message(bot,event.message.message)
                await bot.run_until_disconnected()


    except Exception as e:
        logger.error(msg="Bot failed to start: " + str(e))


asyncio.run(main())
    


