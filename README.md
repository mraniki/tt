# Telegram Trader
 CCXT and Telegram integration. Based on python telegram bot v20. 
 Deploy it via docker. 


[![donate](https://img.shields.io/badge/donate-kofi-orange)](https://imgur.com/a/WQiZcW0) [![github](https://img.shields.io/badge/github-pages-lightgrey)](https://github.com/mraniki/tt)   

[![Docker Pulls](https://img.shields.io/docker/pulls/mraniki/tt?style=plastic)](https://hub.docker.com/r/mraniki/tt).  [![Docker](https://github.com/mraniki/tt/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/docker-publish.yml). [![DockerNightly](https://github.com/mraniki/tt/actions/workflows/docker-image-dev.yml/badge.svg)](https://github.com/mraniki/tt/actions/workflows/docker-image-dev.yml)


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
4) Update bot token / API in the ENV variable or use .env file at the root
5) Submit order to the bot as per the following Order format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY 
  (e.g. `sell BTCUSDT sl=6000 tp=4500 q=1%`) 
 
## ENV Variables:

    #Telegram bot token 
    TOKEN="" 
    #TG user for bot control
    ALLOWED_USER_ID=""
    
    #CCXT supported exchange 
    EXCHANGE1= ""
    ENV SANDBOX_MODE="True"
    #APIKEY
    EXCHANGE1YOUR_API_KEY= ""
    #APISECRET
    EXCHANGE1YOUR_SECRET= "" 
        
        
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


