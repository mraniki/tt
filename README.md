# Talky Trader
 [![](https://badgen.net/badge/icon/TT/E2B13C?icon=bitcoin&label)](https://github.com/mraniki/tt) 
[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)

 CEX & DEX integration with multi messaging platform (Telegram, Matrix and Discord). Query Balance, quote ticker and place order for CEFI and DEFI. Deploy it via docker on cloud platform. 


If you like it, feel free to 
[![donate](https://badgen.net/badge/icon/coindrop/6F4E37?icon=buymeacoffee&label)](https://coindrop.to/mraniki)

Using:

[![telegrambot](https://badgen.net/badge/icon/telegrambot?icon=telegram&label)](https://t.me/pythontelegrambotchannel)
[![pycord](https://badgen.net/badge/icon/pycord?icon=discord&label)](https://github.com/Pycord-Development/pycord)
[![telethon](https://badgen.net/badge/icon/telethon?icon=telegram&label)](https://github.com/LonamiWebs/Telethon)
[![simplematrixbotlib](https://badgen.net/badge/icon/simplematrixbotlib?icon=medium&label)](https://codeberg.org/imbev/simplematrixbotlib)

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
1) Create your channel/room and your platfrom bot 
    - Telegram via [Telegram @BotFather](https://core.telegram.org/bots/tutorial)
    - Discord via [Discord Dev Portal](https://discord.com/developers/docs/intro)
    - Matrix via [Matrix.org](https://turt2live.github.io/matrix-bot-sdk/index.html)
2) Get your 
    - CEX API Keys supported by [CCXT](https://github.com/ccxt/ccxt) or 
    - DEX keys and RPC supported by [Web3](https://github.com/ethereum/web3.py). You can use [chainlist](https://chainlist.org), [awesome rpc list](https://github.com/arddluma/awesome-list-rpc-nodes-providers) or [cointool](https://cointool.app/) for chain/RPC details
3) Update the config (bot token, bot channel and exchange details). Point or copy your config [db.json](config/db.json.sample) to the volume /code/config)
4) Deploy via:
    - docker dockerhub `docker push mraniki/tt:latest` (`docker push mraniki/tt:nightly`)
    - `git clone https://github.com/mraniki/tt:main` and `pip install -r requirements.txt` 
5) Start your container or use `python3 bot.py`

## Config
Quick start approach: Update the sample db with your parameters and save it as db.json. If you deploy the bot on a cloud platform, you can use `DB_URL` environment variable to import db.json from a secure location.

### DB Structure
[DB sample](config/db.json.sample)

### Env
[env sample](config/env.sample)

## Bot commands
 - `sell BTCUSDT sl=6000 tp=4500 q=1%` or `sell BTCUSDT` Order processing (direction symbol sl=stoploss tp=takeprofit q=percentagequantity% or direction symbol)
 - `/bal` Query user account exchange balance
 - `/cex name` or `/dex name` Switch between any CEX or DEX (e.g `/cex binance`, `/cex kraken`, `/dex pancake`, `/dex quickswap`)
 - `/trading` Disable or Enable trading
 - `/testmode` Switch between testnet,sandbox or mainnet  
 - `/q BTCB` Retrieve ticker quote and token information from exchange and coingecko

## Features Available
 
 ### v1 
 - Enable bot in Telegram (ptb v20 and telethon), Matrix (simplematrixbotlib) and Discord (pycord) messaging platform
 - Place order for CEX and DEX, Query Balance and quote ticker
 - Push your order signal manually or from system like trading view webhook (verified with Binance, Binance Testnet and ~~FTX😠~~ Kraken, BSC & pancakeswap, polygon and quickswap). If SL / TP or QTY are missing values are defaulted
 - Support DEX automatic token approval
 - Support uniswap v2, 1inch api and uniswap v3 swap methods
 - Support % of stablecoin balance when placing order
 
 ### Other Features
 - Support bot in private channel and multiple channel per environment
 - Support multiple environment via variable (e.g. DEV, PRD, PRD CEX, UNI1 or UNI2)
 - Handle messaging in one function across messaging platforms using HTML format
 - Handle libraries exceptions in one function and notification delivery with apprise 
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub
 - Support deployment on  or selfhosting 
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config
 - Support config file as variable to deploy on [PaaS](https://github.com/ripienaar/free-for-dev#paas) (tested with northflank, render or fly.io)
 - Create DB if it is missing and check bot variables for failover
 - Support bot restart capability
 - Support standard json [tokenlist.org](tokenlist.org) search for testnet DEX support [(example)](https://github.com/mraniki/tokenlist/blob/main/testnet.json)
 - Convert symbol to DEX checksum address via coingecko API to support any symbol and any chain listed in coingecko
 - Configure the default exchange and default test mode when starting the bot.
 - Support multiple messaging platform (Telegram, Matrix and Discord) 

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)


## 🚧 Roadmap


### V1.3
- Support Uniswap V3 (more testing needed)

### v1.4
- Support limit order for DEX (1inch and v3)
- Support DEX limit order if supported like dydx / Kwenta / GMX
- Review testmode command to be part of the switch command.

### v1.5

- Support futures and margin for CEX (to be tested via CCXT)
- Support STOPLOSS TAKEPROFIT for CEX
- Support multiple TAKEPROFIT target for CEX
- View free margin for futures in /bal
- View opened position via /pos (futures and limit order)

### v2 backlog
- Create / modify db via bot chat nested conversation
- Review DEX private key strategy (walletconnect authentification via pywalletconnect)
- Support Web3 ENS
- View daily pnl in /bal
- View weekly pnl with /w command and scheduling

### v3 backlog
- Merge with MQL4 bot version integrated with MT4 exchanges for TradFi support[![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/) 


 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK**. For DEX, Never share your private keys.
 
 **NEVER use your main account for automatic trade**
