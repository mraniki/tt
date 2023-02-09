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
    - DEX chain supported by [Web3](https://github.com/ethereum/web3.py). You can use [chainlist](https://chainlist.org), [awesome rpc list](https://github.com/arddluma/awesome-list-rpc-nodes-providers) or [cointool](https://cointool.app/) for chain details
3) Update the config (telegram token and telegram channel). Point your config to container volume /code/config)
4) Deploy :
    - via docker dockerhub `docker push mraniki/tt:latest` (or `docker push mraniki/tt:nightly`) or
    - `git clone https://github.com/mraniki/tt:main` and `pip install -r requirements.txt` 
5) Start your container or use `python3 bot.py`

## Config
Approach:
- Update the sample db with your parameters and save it as db.json
- if you deploy the bot on a cloud platform, you can use `DB_URL` to import db.json

### Env
[env sample](config/env.sample)

### DB Structure
[DB sample](config/db.json.sample)

### Bot commands
 - Disable or Enable trading via `/trading` 
 - Query account balance via `/bal`
 - Query ticker price via `/q BTCB` to view exchange and coingecko quotes.
 - Get coingecko token information via `/coin BTC`
 - Switch between any CEX or DEX in one environment with prefix `/cex exchangename` or `/dex exchangename` (e.g `/cex binance`, `/cex kraken`, `/dex pancake`, `/dex quickswap`)
 - Switch test and mainnet with `/testmode` 
 
### Features Available
 
 ### v1 
 - Enable bot in pythontelegram v20 and support CEX and DEX exchange formatted error via telegram
 - Query Balance, quote ticker and place order for CEX and DEX
 - Push your order signal manually or from system like trading view webhook (via n8n or ngrok) to submit order with `sell BTCUSDT sl=6000 tp=4500 q=1%` for CEFI and DEFI (verified with Binance, Binance Testnet and ~~FTX~~ Kraken, BSC & pancakeswap, polygon and quickswap). If SL / TP or QTY are missing (e.g. `sell BTCUSDT`) values are defaulted
 - Support DEX automatic token approval
 - Support uniswap v2, 1inch api and uniswap v3 swap methods
 - Support % of balance when placing order
 - Convert symbol to checksum address via coingecko API to support any symbol and any chain listed in coingecko
 - Able to start the bot with any exchange as default option. 
 
 ### Other Features
 - Support bot in private channel (or private chat) and multiple channel per enviroment
 - Support multiple environment via variable (e.g. DEV, PRD, PRD CEX, UNI1 or UNI2)
 - Handle messaging in one function
 - Handle libraries exceptions in one function and delivery with apprise to support more notification system
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config
 - support config file as variable to ease deployment on cloud platform
 - Create DB as the start if it is missing and connect to default DEX
 - Support restart capability
 - Support standard json tokenlist search for testnet support more info on [tokenlist.org](tokenlist.org)

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)

 ## 🚧 Roadmap


### V1.3
- Support Uniswap V3

### v1.4
- Review PrivateKey strategy

### v1.5

- Support limit order for DEX
- Support Web3 ENS

### v2 backlog

- Support DEX limit order if supported like dydx / Kwenta / GMX
- Support futures and margin for CEX (to be tested via CCXT)
- Support STOPLOSS TAKEPROFIT for CEX
- create / modify db via bot chat nexted command
- view daily pnl in /bal response
- view free margin for futures in /bal response
- view opened future position via /pos command
- Support bot in webhook instead of getupdate
- View weekly pnl with /w command

### v3 backlog
- [![Matrix](https://badgen.net/badge/icon/matrix/black?icon=libraries&label)](https://github.com/poljar/matrix-ni) Integrate with agnostic chat bot system 
- [![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/) Merge with Telegram MQL4 version which integrate with MT4 exchanges for TradFi support


 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK**. For DEX, Never share your private keys.

 **NEVER use your main account for automatic trade**
