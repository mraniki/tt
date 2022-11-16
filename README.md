# Telegram Trader
 CEX, DEX and Telegram integration. Based on python telegram bot v20. 
 Deploy it via docker. 

[![](https://badgen.net/badge/icon/TT/E2B13C?icon=bitcoin&label)](https://github.com/mraniki/tt)
[![donate](https://badgen.net/badge/icon/coindrop/6F4E37?icon=buymeacoffee&label)](https://coindrop.to/mraniki) 
[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)



Built with
[![telegrambot](https://badgen.net/badge/icon/telegrambot?icon=telegram&label)](https://t.me/pythontelegrambotchannel)
[![ccxt](https://badgen.net/badge/icon/ccxt/black?icon=libraries&label)](https://github.com/ccxt/ccxt)
[![Web3](https://badgen.net/badge/icon/web3/black?icon=libraries&label)](https://github.com/ethereum/web3.py)
[![sublime](https://badgen.net/badge/icon/sublime/F96854?icon=terminal&label)](https://www.sublimetext.com/)
[![workingcopy](https://badgen.net/badge/icon/workingcopy/16DCCD?icon=github&label)](https://workingcopy.app/)

## Build status
[![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml) [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml)

## Install
1) Create a private channel and a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Get your API Keys supported by [CCXT](https://github.com/ccxt/ccxt). 
3) Update the config (as per below), bot token, API in the .env file in config (and point your env file to container volume /code/config)
4) Deploy :
- via docker dockerhub (or ghcr.io) `docker push mraniki/tt:latest` or `docker push mraniki/tt:nightly`
- or `git clone https://github.com/mraniki/tt:main` and `pip install -r requirements.txt`
6) Start your container
7) Submit order to the bot as per the following Order format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY 
  (e.g. `sell BTCUSDT sl=6000 tp=4500 q=1%`) 

## Config
Either use .env file, environment docker compose variable or json db as per below structure.
Environment file or docker variable are loaded in db at the startup.

### Env
[env sample](config/env.sample)

### DB Structure
[DB sample](config/db.json.sample)

 ## Features
 - Enable bot in pythontelegram v20 and support exchange formatted error via telegram
 - Push your signal manually or from system like trading view webhook to submit order to your ccxt exchange and receive confirmation
 - Disable or Enable trading process via /trading command
 - Query balance via /bal command and view it in formatted way
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub and github container repo
 - Support multiple enviroment, testnet and production exchange via environment variable file
 - Support % of USDT balance for order
 - Support bot in private channel (or private chat) and multiple channel per enviroment
 - Handle Multi CEFI config (verified with Binance, Binance Testnet and ~~FTX~~ Kraken) and DEFI (test with Pancake)
 - Switch between CEFI using `/cex binance` or `/cex kraken` or DEFI `/dex pancake`
 - Support config folder and config file in the dockerfile to automatically create the volume folder and its config

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)

 ## 🚧 Roadmap
v1
- Integrate DEFI DEX (like pancakeswap or uniswap)
- support futures and margin 
- Setup send message overall function
- clean up and refactorize the code structure for clean v1
- view opened future position via /pos command 
v2
- Integrate with Matrix to be messaging platform agnostic [![matrix](https://badgen.net/badge/icon/nio/black?icon=libraries&label)](https://github.com/poljar/matrix-nio)
- view last closed orders via /order command 
- view daily pnl and free margin in /bal response
v3
- Merge with Telegram MQL4 version which integrate with MT4 exchanges [![mql](https://badgen.net/badge/icon/mql/black?icon=libraries&label)](https://mql5.com/)

 ## ⚠️ Disclaimer
 This is an education tool and should not be considered professional financial investment system nor financial advice. Use a testnet account or **USE AT YOUR OWN RISK**

