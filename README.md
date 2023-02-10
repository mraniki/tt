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
[![coingecko](https://badgen.net/badge/icon/coingecko/black?icon=libraries&label)](https://github.com/coingecko)

[![sublime](https://badgen.net/badge/icon/sublime/F96854?icon=terminal&label)](https://www.sublimetext.com/)
[![workingcopy](https://badgen.net/badge/icon/workingcopy/16DCCD?icon=github&label)](https://workingcopy.app/)

## Build status
[![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml) [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Nightly.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Nightly.yml)

## Install
1) Create a private channel and a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Get your 
    - CEX API Keys supported by [CCXT](https://github.com/ccxt/ccxt) or 
    - DEX keys and RPC supported by [Web3](https://github.com/ethereum/web3.py). You can use [chainlist](https://chainlist.org), [awesome rpc list](https://github.com/arddluma/awesome-list-rpc-nodes-providers) or [cointool](https://cointool.app/) for chain details
3) Update the config (bot token, bot channel and exchange details). Point or copy your config [db.json](config/db.json.sample) to the volume /code/config)
4) Deploy via:
    - docker dockerhub `docker push mraniki/tt:latest` (or `docker push mraniki/tt:nightly`) or
    - `git clone https://github.com/mraniki/tt:main` and `pip install -r requirements.txt` 
5) Start your container or use `python3 bot.py`

## Config
Quick start approach: Update the sample db with your parameters and save it as db.json. If you deploy the bot on a cloud platform, you can use `DB_URL` environment variable to import db.json from a secure location.

### DB Structure
[DB sample](config/db.json.sample)

### Env
[env sample](config/env.sample)

## Bot commands
 - `/bal` Query user account exchange balance
 - `/cex name` or `/dex name` Switch between any CEX or DEX (e.g `/cex binance`, `/cex kraken`, `/dex pancake`, `/dex quickswap`)
 - `/trading` Disable or Enable trading
 - `/testmode` Switch between testnet,sandbox or mainnet  
 - `/q BTCB` Retrieve ticker quote from exchange and coingecko.
 - `/coin BTC` Get coingecko token information

## Features Available
 
 ### v1 
 - Enable bot in pythontelegram v20 and support CEX and DEX exchange formatted error via telegram
 - Query Balance, quote ticker and place order for CEX and DEX
 - Push your order signal manually or from system like trading view webhook (via n8n or ngrok) to submit order with `sell BTCUSDT sl=6000 tp=4500 q=1%` for CEFI and DEFI (verified with Binance, Binance Testnet and ~~FTX~~ Kraken, BSC & pancakeswap, polygon and quickswap). If SL / TP or QTY are missing (e.g. `sell BTCUSDT`) values are defaulted
 - Support DEX automatic token approval
 - Support uniswap v2, 1inch api and uniswap v3 swap methods
 - Support % of balance when placing order
 
 ### Other Features
 - Support bot in private channel (or private chat) and multiple channel per environment
 - Support multiple environment via variable (e.g. DEV, PRD, PRD CEX, UNI1 or UNI2)
 - Handle messaging in one function
 - Handle libraries exceptions in one function and notification delivery with apprise 
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config
 - Support config file as variable to deploy on cloud platform (like northflank, render or fly.io)
 - Create DB if it is missing and connect to default DEX
 - Support bot restart capability
 - Support standard json [tokenlist.org](tokenlist.org) search for testnet DEX support
 - Convert symbol to DEX checksum address via coingecko API to support any symbol and any chain listed in coingecko
 - Configured the default exchange and default test mode when starting the bot. 

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)


## 🚧 Roadmap


### V1.3
- Support Uniswap V3

### v1.4
- Support limit order for DEX (1inch and v3)

### v1.5

- Review DEX private key strategy (wallet authentification)

### v2 backlog

- Support DEX limit order if supported like dydx / Kwenta / GMX
- Support Web3 ENS
- Support futures and margin for CEX (to be tested via CCXT)
- Support STOPLOSS TAKEPROFIT for CEX
- create / modify db via bot chat nested conversation
- view daily pnl in /bal response
- view free margin for futures in /bal
- view opened position via /pos (futures and limit order)
- Support bot in webhook instead of getupdate
- View weekly pnl with /w command and scheduling

### v3 backlog
- Simplify the integration with any chat bot system [![Matrix](https://badgen.net/badge/icon/matrix/black?icon=libraries&label)](https://github.com/poljar/matrix-ni), RocketChat or others.
- Merge with MQL4 bot version integrated with MT4 exchanges for TradFi support[![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/) 


 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK**. For DEX, Never share your private keys.
 
 **NEVER use your main account for automatic trade**
