# Telegram Trader
 CCXT and Telegram integration. Based on python telegram bot v20. 
 Deploy it via docker. 

[![](https://badgen.net/badge/icon/TT/E2B13C?icon=bitcoin&label)](https://github.com/mraniki/tt)
[![donate](https://badgen.net/badge/icon/coindrop/6F4E37?icon=buymeacoffee&label)](https://coindrop.to/mraniki) 

[![github](https://badgen.net/badge/icon/github/grey?icon=github&label)](https://github.com/mraniki/tt) 
[![Docker Pulls](https://badgen.net/docker/pulls/mraniki/tt)](https://hub.docker.com/r/mraniki/tt)



Made with
[![telegrambot](https://badgen.net/badge/icon/telegrambot?icon=telegram&label)](https://t.me/pythontelegrambotchannel)
[![ccxt](https://badgen.net/badge/icon/ccxt/black?icon=libraries&label)](https://github.com/ccxt/ccxt)
[![sublime](https://badgen.net/badge/icon/sublime/F96854?icon=terminal&label)](https://www.sublimetext.com/)
[![workingcopy](https://badgen.net/badge/icon/workingcopy/16DCCD?icon=github&label)](https://workingcopy.app/)

## Build status
[![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml) [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml)

## Install
1) Create a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Create your API Keys supported by [CCXT](https://github.com/ccxt/ccxt). 
3) Deploy :
- via docker 
  - dockerhub `docker push mraniki/tt:latest` or `docker push mraniki/tt:nightly`,
  - or github `docker pull ghcr.io/mraniki/tt:main` or `docker pull ghcr.io/mraniki/tt:nightly`
- or `git clone https://github.com/mraniki/tt:main`
4) Update bot token, API in the .env file in config (and point your env file to container volume /code/config)
5) Start your container
6) Submit order to the bot as per the following Order format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY 
  (e.g. `sell BTCUSDT sl=6000 tp=4500 q=1%`) 
  
        ##ENV Variables:
        TG_TOKEN=""
        TG_USER_ID=""

        #CCXTsupported exchange details
        #CCXTSANDBOX details
        TEST_SANDBOX_MODE="True"
        TEST_SANDBOX_EXCHANGE_NAME="binance"
        TEST_SANDBOX_YOUR_API_KEY=""
        TEST_SANDBOX_YOUR_SECRET=""
        TEST_SANDBOX_ORDERTYPE="MARKET" 

        #PROD APIKEY Exchange1
        EXCHANGE1_NAME="binance"
        EXCHANGE1_YOUR_API_KEY=""
        EXCHANGE1_YOUR_SECRET=""
        EXCHANGE1_ORDERTYPE="MARKET" 

        
 ## Use Case
 - Enable bot in pythontelegram v20 and support exchange raw error via telegram
 - Push your signal manually or from system like trading view webhook to submit order to your ccxt exchange and receive confirmation
 - Disable or Enable trading process via /trading command
 - Query balance via /bal command and view it in formatted way
 - Enable dev and main branches with auto release and docker deployment pipeline setup for continueous deployment in dockerhub and github container repo
 - Support testnet and prod exchange via environment variable file
 - Support % of balance for order
 
![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)

 ## 🚧 ToDo
- formating/handling of response from exchange (opened position, last closed order)
- formatting/handling of error from bot and from exchange api
- add config folder in the dockerfile to automatically create the volume folder
- support futures and margin options
- view last closed orders via /order command 
- view opened future position via /pos command 
- view daiky pnl via /profit or /bal command
- handle 2/multi exchanges at the same time
- Test across multiple key exchanges (Binance, Coinbase, FTX, Kraken, Kucoin and Huobi)
- Merge with Telegram MQL4 version which integrate with MT4 exchanges

 ## ⚠️ Disclaimer
 This is a tool and should not be considered professional financial investment system nor financial advice.
Use a testnet account or **USE AT YOUR OWN RISK**

