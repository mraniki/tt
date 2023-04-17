# Talky Trader



[![Logo](https://i.imgur.io/Q7iDDyB_d.webp?maxwidth=640&shape=thumb&fidelity=medium)](https://github.com/mraniki/tt)<img width="340" alt="Screenshot 2023-02-28 at 20 39 47" src="https://user-images.githubusercontent.com/8766259/222161597-114d488b-ad9c-4468-8dd4-083f435cbb7b.png"><img width="388" alt="Screenshot 2023-03-05 at 10 51 04" src="https://user-images.githubusercontent.com/8766259/222953459-0aaf024b-4d7b-4a57-b31b-7cab08f3c0d3.png">

[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)

 CEX & DEX integration with multi messaging platform support (Telegram, Matrix and Discord). Place order for CEFI or DEFI exchanges, query balance and quote ticker. Deploy it via docker on selfhosted platform or PaaS. 

 
[![telegrambot](https://badgen.net/badge/icon/telegrambot?icon=telegram&label)](https://t.me/pythontelegrambotchannel)
[![telethon](https://badgen.net/badge/icon/telethon?icon=telegram&label)](https://github.com/LonamiWebs/Telethon)
[![pycord](https://badgen.net/badge/icon/pycord/purple?icon=discord&label)](https://github.com/Pycord-Development/pycord)
[![simplematrixbotlib](https://badgen.net/badge/icon/simplematrixbotlib/grey?icon=medium&label)](https://codeberg.org/imbev/simplematrixbotlib)

[![python3.10](https://badgen.net/badge/icon/3.10/black?icon=pypi&label)](https://www.python.org/downloads/release/python-3100/)
[![ccxt](https://badgen.net/badge/icon/ccxt/black?icon=libraries&label)](https://github.com/ccxt/ccxt)
[![dxsp](https://badgen.net/badge/icon/dxsp?icon=pypi&label)](https://pypi.org/project/dxsp/)

[![tinyDB](https://badgen.net/badge/icon/tinyDB/black?icon=libraries&label)](https://github.com/msiemens/tinydb)
[![apprise](https://badgen.net/badge/icon/apprise/black?icon=libraries&label)](https://github.com/caronc/apprise) [![FastAPI](https://badgen.net/badge/icon/fastapi/black?icon=libraries&label)](https://github.com/tiangolo/fastapi)



[![sublime](https://badgen.net/badge/icon/sublime/F96854?icon=terminal&label)](https://www.sublimetext.com/)
[![workingcopy](https://badgen.net/badge/icon/workingcopy/16DCCD?icon=github&label)](https://workingcopy.app/)

If you like it, feel free to 
[![donate](https://badgen.net/badge/icon/coindrop/6F4E37?icon=buymeacoffee&label)](https://coindrop.to/mraniki)

## Build status
[![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml) [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Nightly.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Nightly.yml)

## Install
1) Create your channel/room and your platform bot 
    - Telegram via [Telegram @BotFather](https://core.telegram.org/bots/tutorial) if you use Telethon [create an api key](https://docs.telethon.dev/en/stable/basic/signing-in.html) 
    - Discord via [Discord Dev Portal](https://discord.com/developers/docs/intro)
    - Matrix via [Matrix.org](https://turt2live.github.io/matrix-bot-sdk/index.html)
2) Get your 
    - CEX API Keys supported by [CCXT](https://github.com/ccxt/ccxt) or 
    - DEX keys and RPC supported by [Web3](https://github.com/ethereum/web3.py). You can use [chainlist](https://chainlist.org), [awesome rpc list](https://github.com/arddluma/awesome-list-rpc-nodes-providers) or [cointool](https://cointool.app/) for chain/RPC details
3) Update the config (bot token, bot channel and exchange details). Point or copy your config [db.json](config/db.json.sample) to the volume /code/config)
4) Deploy via:
    - docker `docker push mraniki/tt:latest` or `docker pull ghcr.io/mraniki/tt:latest`
    - locally `git clone https://github.com/mraniki/tt:main` && `pip install -r requirements.txt` 
5) Start your container or if deployed locally use `python3 bot.py` to start

6) More details in [Wiki](https://github.com/mraniki/tt/wiki)

## Config
Quick start approach: Update the sample db with your parameters and save it as db.json. If you deploy the bot on a PaaS cloud platform, you can use `DB_URL` environment variable to import db.json from a secure location.
MOre detail on the config: https://github.com/mraniki/tt/wiki/Configuration

### DB Structure
[DB sample](config/db.json.sample)

### Env
[env sample](config/env.sample)

## Bot commands
 - `sell BTCUSDT sl=6000 tp=4500 q=1%` or `sell BTCUSDT` Order processing (direction symbol sl=stoploss tp=takeprofit q=percentagequantity% or direction symbol)
 - `/bal` Query user account exchange balance
 - `/cex name` or `/dex name` Switch between any CEX or DEX (e.g `/cex kraken`, `/dex pancake`)
 - `/trading` Disable or Enable trading
 - `/testmode` Switch between testnet,sandbox or mainnet  
 - `/q BTCB` Retrieve ticker quote and token information from exchange and coingecko

## Features Available
 
 ### v1 
 - Enable bot in Telegram (ptb v20 and telethon), Matrix (simplematrixbotlib) and Discord (pycord) messaging platform
 - Place order for CEX and DEX, Query Balance and quote ticker
 - Push your order signal manually or from system like [trading view webhook alert](https://www.tradingview.com/pine-script-docs/en/v5/concepts/Alerts.html#using-all-alert-calls). Verified with Binance, Binance Testnet, ~~FTX😠~~, Kraken, Huobi, BSC & pancakeswap, polygon and quickswap). If SL / TP or QTY are missing values are defaulted
 - Support DEX automatic token approval
 - Support uniswap v2 and 1inch api
 - Support % of stablecoin balance when placing order
 
 ### Other Features
 - Support bot in private channel and multiple channel per environment
 - Support multiple environment via variable (e.g. DEV, PRD, PRD CEX, UNI1 or UNI2)
 - Handle libraries exceptions in one function and notification delivery with apprise 
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub
 - Support all messaging bot as asynchrousnous process
 - Support common notification via Apprise for all nessaging platform
 - Support deployment on PaaS or selfhosting 
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config
 - Support config file as variable to deploy on [PaaS](https://github.com/ripienaar/free-for-dev#paas) (tested with northflank, koyeb, GKE, render and fly.io)
 - Create DB if it is missing and check bot variables for failover
 - Support bot restart capability
 - Support contract with standard json [tokenlist.org](tokenlist.org) [vetted tokenlist](https://github.com/viaprotocol/tokenlists), personal list for testnet [(example)](https://github.com/mraniki/tokenlist/blob/main/testnet.json)
 - Support coingecko API as backup of tokenlist for contract search
 - Configure the default exchange and default test mode when starting the bot.
 - Support multiple messaging platform (Telegram, Matrix and Discord)
 - Include healthcheck, webhook and notify capability via FastAPI webserver on port 8080 with build-in JSON API swagger

## WIKI

 [Wiki](https://github.com/mraniki/tt/wiki)

## Questions? Want to help? 

[![discord](https://badgen.net/badge/icon/discord/purple?icon=discord&label)](https://discord.gg/vegJQGrRRa)
[![telegram](https://badgen.net/badge/icon/telegram?icon=telegram&label)](https://t.me/TTTalkyTraderChat/1)


## 📷 Screenshots
<img width="340" alt="Screenshot 2023-02-28 at 20 39 47" src="https://user-images.githubusercontent.com/8766259/222161597-114d488b-ad9c-4468-8dd4-083f435cbb7b.png">

[more screenshots](https://github.com/mraniki/tt/wiki/Screenshots)

## 🚧 Roadmap

[🚧 Roadmap](https://github.com/mraniki/tt/milestones)

### V1.3

- Refactoring of more complex functions

### v1.4

- Support Uniswap V3 
- Support limit order for DEX (1inch) and review feasibility for dydx / GMX
- Review testmode command to be part of the switch command


### v1.5

- Support limit order for DEX (Uniswap v3) 
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
- Merge with MQL4 version for MT4 TradFi support[![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/) 


 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK**. For DEX, Never share your private keys.
 
 **NEVER use your main account for automatic trade**
