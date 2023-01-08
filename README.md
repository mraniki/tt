# Telegram Trader
 [![](https://badgen.net/badge/icon/TT/E2B13C?icon=bitcoin&label)](https://github.com/mraniki/tt) 
[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)

 CEX, DEX and Telegram integration. Query Balance, quote ticker and place order for CEFI and DEFI.
 Based on python telegram bot v20, CCXT, Web3 v6 and TinyDB.
 Deploy it via docker. 


If you like it, feel free to 
[![donate](https://badgen.net/badge/icon/coindrop/6F4E37?icon=buymeacoffee&label)](https://coindrop.to/mraniki)

Using:

[![telegrambot](https://badgen.net/badge/icon/telegrambot?icon=telegram&label)](https://t.me/pythontelegrambotchannel)

[![python3.10](https://badgen.net/badge/icon/3.10/black?icon=pypi&label)](https://www.python.org/downloads/release/python-3100/)
[![ccxt](https://badgen.net/badge/icon/ccxt/black?icon=libraries&label)](https://github.com/ccxt/ccxt)
[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py)
[![tinyDB](https://badgen.net/badge/icon/tinyDB/black?icon=libraries&label)](https://github.com/msiemens/tinydb)
[![apprise](https://badgen.net/badge/icon/apprise/black?icon=libraries&label)](https://github.com/caronc/apprise)


[![sublime](https://badgen.net/badge/icon/sublime/F96854?icon=terminal&label)](https://www.sublimetext.com/)
[![workingcopy](https://badgen.net/badge/icon/workingcopy/16DCCD?icon=github&label)](https://workingcopy.app/)

## Build status
[![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml) [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml)

## Install
1) Create a private channel and a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Get your 
    - CEX API Keys supported by [CCXT](https://github.com/ccxt/ccxt) or 
    - DEX chain supported by [Web3](https://github.com/ethereum/web3.py). You can use [chainlist](https://chainlist.org) or [awesome rpc list](https://github.com/arddluma/awesome-list-rpc-nodes-providers) for RPC detail per chain.
3) Update the config (telegram token, API, router). Point your config to container volume /code/config)
4) Deploy :
    - via docker dockerhub (or ghcr.io) `docker push mraniki/tt:latest` (or `docker push mraniki/tt:nightly`) or
    - `git clone https://github.com/mraniki/tt:main` and `pip install -r requirements.txt` 
5) Start your container or use `python3 bot.py`
6) `sell BTCUSDT sl=6000 tp=4500 q=1%` or for DEFI `BUY BTCB` to place order as per format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY
7) `/bal` command to query balance
8) `/price BTCB` or `/price btc/usdt` to query ticker price 
9) `/cex exchangename` or `/dex exchangename` (e.g `/cex binance`, `/dex quickswap`) to switch between multiple CEX and DEX with prefix 
10) `/testmode` to switch between sandbox, mainnet, testnet
11) `/trading` to disable/enable trading

## Config
Either use .env file or json db as per below structure. Environment file or docker variable are automatically loaded in a new db at the startup if there is no DB.
Approach: Do an initial launch to have the DB structure created automatically and add your telegram bot details or update the DB sample.

### Env
[env sample](config/env.sample)

### DB Structure
[DB sample](config/db.json.sample)

 ## Features Available
 
 ### v1 
 - Enable bot in pythontelegram v20 and support CEX and DEX exchange formatted error via telegram
 - Query Balance, quote ticker and place order for CEX and DEX
 - Push your order signal manually or from system like trading view webhook (via n8n or ngrok) to submit order with `sell BTCUSDT sl=6000 tp=4500 q=1%` for CEFI and DEFI (verified with Binance, Binance Testnet and ~~FTX~~ Kraken, BSC & pancakeswap, polygon and quickswap). If SL / TP or QTY are missing (`sell BTCUSDT`) values are defaulted
 - Disable or Enable trading process via `/trading` command
 - Query balance via `/bal` command and view it in formatted way
 - Query ticker price via `/price BTCB` or `/price btc/usdt` command to view last symbol price (USDT as basis)
 - Switch between multiple CEX and DEX in one environment with prefix `/cexexchange name` or `/dex exchange name` (e.g `/cex binance`, `/cex kraken`, `/dex pancake`, `/dex quickswap`)
 - Switch between testnet and mainnet with `/testmode` 
 - Support % of USDT balance for CEX order
 - Support standard DEX token list per exchange (e.g. [https://tokenlists.org/](tokenlist.org)) with function to convert symbol to checksum address from the token list
 
 ### Other Features
 - Support bot in private channel (or private chat) and multiple channel per enviroment
 - Support multiple environment via variable (e.g. DEV, PRD or PRD DEX / PRD CEX)
 - Handle messaging in one function
 - Handle libraries exceptions in one function and delivery with apprise to support more notification system
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub and github container repo
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config
 - Start up simplified to create DB if it is missing

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)

 ## 🚧 Roadmap

### V1.2

- Better error handling
- More testing and code hardening

### V1.3
- Simplify the Exchange search functions
- Add Base currency at exchange variable (like USDT/USDC/BUSD or others)
- Allow to start with DEX for initial start
- Support DEFI DEX uniswap and dydx (to be tested)
- Support DEX limit order if supported like dydx

### v1.4
- create / modify db via bot command

### v1.5

- Support futures and margin for CEX (to be tested)
- Support Web3 ENS

### v2
- view daily pnl in /bal response
- view free margin for futures in /bal response
- view opened future position via /pos command
- Support bot in webhook instead of getupdate
- View weekly pnl with /w command

### v3
- [![Matrix](https://badgen.net/badge/icon/matrix/black?icon=libraries&label)](https://github.com/poljar/matrix-ni) Integrate with agnostic chat bot  platform 
- [![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/) Merge with Telegram MQL4 version which integrate with MT4 exchanges for TradFi support


 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK** 

 **NEVER use your main account for automatic trade**
