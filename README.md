# Telegram Trader
 CCXT and Telegram integration. Based on python telegram bot v20. 
 Deploy it via docker. 


[![donate](https://img.shields.io/badge/donate-kofi-orange)](https://imgur.com/a/WQiZcW0) [![github](https://img.shields.io/badge/github-pages-lightgrey)](https://github.com/mraniki/tt)   


[![Docker Pulls](https://img.shields.io/docker/pulls/mraniki/tt?style=plastic)](https://hub.docker.com/r/mraniki/tt).  [![Docker](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub.yml). [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/DockerHub_Dev.yml)



[![telegrambot](https://img.shields.io/badge/Telegram-Channel-blue.svg?logo=telegram)](https://t.me/pythontelegrambotchannel)
[![Twitter Follow](https://img.shields.io/twitter/follow/ccxt_official.svg?style=social&label=CCXT)](https://twitter.com/ccxt_official)

## Install
1) Create a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Create your API Keys supported by CCXT https://github.com/ccxt/ccxt. Use testnet account for testing this tool.
3) Deploy :
- via docker 
  - dockerhub `docker push mraniki/tt:latest` or nightly,
  - or github `docker pull ghcr.io/mraniki/tt:main` for latest stable or `docker pull ghcr.io/mraniki/tt:dev` for nightly
- or `git clone https://github.com/mraniki/tt`
4) Update bot token / API in the .env file in /config
5) Start your container
6) Submit order to the bot as per the following Order format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY 
  (e.g. `sell BTCUSDT sl=6000 tp=4500 q=1%`) 
 
## ENV Variables:

     #Telegram bot token 
     ENV TELEGRAM_TOKEN="" 
     #TG user for bot control
     ENV TELEGRAM_ALLOWED_USER_ID=""

     #CCXT supported exchange details

     #CCXT SANDBOX details
     ENV TEST_SANDBOX_MODE="True"
     ENV TEST_SANDBOX_EXCHANGE_NAME="binance"
     ENV TEST_SANDBOX_YOUR_API_KEY= "" 
     ENV TEST_SANDBOX_YOUR_SECRET=""
     ENV TEST_SANDBOX_ORDERTYPE="market"

     #PROD APIKEY Exchange1
     ENV EXCHANGE1_NAME="binance"
     ENV EXCHANGE1_YOUR_API_KEY= ""
     ENV EXCHANGE1_YOUR_SECRET=""
     ENV EXCHANGE1_ORDERTYPE="market" 
        
        
 ## Use Case
 - Push your signal manually or from system like trading view webhook to submit order to your ccxt exchange
 - Disable or Enable trading process via /trading command
 - Query balance via /bal command

![IMG_2517](https://user-images.githubusercontent.com/8766259/199422978-dc3322d9-164b-42af-9cf2-84c6bc3dae29.jpg)


 ## toDo
- formating/handling of response from exchange (bal, opened position, last closed order)
- support % of balance for order
- support testnet via variable 
- formating/handling of error from bot and from exchange api
- view opened orders/position via /order command 
- handle 2/multi exchanges
- Merge with MQL4 version which integrate with MT4 exchanges (reach out if you are interested)


