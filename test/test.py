import os
from dotenv import load_dotenv
import asyncio
from web3 import Web3
#import many_abis as ma


#YOUR VARIABLES
load_dotenv()
#chain ID being used refer to https://chainlist.org/
chain_id = os.getenv("CHAIN_ID", 10)

#your wallet details
wallet_address = os.getenv("WALLET_ADDRESS", "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
private_key = os.getenv("PRIVATE_KEY", "0x111111111117dc0aa78b770fa6a738034120c302")

#1 for 1inch and 2 for Uniswap V2
protocol = os.getenv("PROTOCOL", 1)

#DATA from MANY_ABIS FOR RPC and EXCHANGE
chain = ma.get_chain_by_id(chain_id=int(chain_id))
network_provider_url = os.getenv("NETWORK_PROVIDER_URL", chain['rpc'][0])
dex_exchange = os.getenv("DEX_EXCHANGE", 'Uniswap V2')
amount_trading_option = os.getenv("AMOUNT_TRADING_OPTION", 1)

#Block explorer API from ETHERSCAN TYPE EXPLORER
block_explorer_api = os.getenv("BLOCK_EXPLORER_API", "1X23Q4ACZ5T3KXG67WIAH7X8C510F1972TM")

#DEX CONNECTIVITY
w3 = Web3(Web3.HTTPProvider(network_provider_url))

from dxsp import DexSwap

async def main():
	#SWAP HELPER
	print(w3,chain_id,wallet_address,private_key,protocol,dex_exchange,amount_trading_option,block_explorer_api)
	dex = DexSwap(w3,chain_id,wallet_address,private_key,protocol,dex_exchange,amount_trading_option,block_explorer_api=block_explorer_api)

	#get Contract Address
	bitcoinaddress = await dex.search_contract('wBTC')
	print("bitcoinaddress ", bitcoinaddress)
	#bitcoinaddress  0x68f180fcCe6836688e9084f035309E29Bf0A2095
	# check : https://optimistic.etherscan.io/token/0x68f180fcce6836688e9084f035309e29bf0a2095?a=0x5bb949b4938aaf1b2e97f4871a8968a4abea7c98

	#getABI
	bitcoinaddressABI = await dex.get_abi(bitcoinaddress)
	print(bitcoinaddressABI)

	#QUOTE
	quote = await dex.get_quote('wBTC')
	print("quote ", quote)

	#BUY 10 USDC of BITCOIN
	demo_tx = await dex.get_swap('USDC','wBTC',10)
	print("demo_tx ", demo_tx)

	#NORMAL SWAP
	# transaction_amount_out = 10
	# asset_out_symbol = "USDT"
	# asset_in_symbol = "ETH"
	#SWAP EXECUTION
	# transaction = await dex.get_swap(transaction_amount_out,asset_out_symbol,asset_in_symbol)
	# print("transaction ", transaction)

if __name__ == "__main__":
    asyncio.run(main())
