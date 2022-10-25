# Telegram Trader
Based on python telegram bot v20
Deploy it via docker. 

## Install

    docker pull ghcr.io/mraniki/tt:main

## ENV Variables:

    #Telegram bot token via [@BotFather ](https://core.telegram.org/bots/tutorial)
    TOKEN="" 
    #TG user for bot control
    ALLOWED_USER_ID=""
    
    #CCXT supported exchange via https://github.com/ccxt/ccxt
    EXCHANGE1= ""
    #APIKEY
    EXCHANGE1YOUR_API_KEY= ""
    #APISECRET
    EXCHANGE1YOUR_SECRET= "" 
 
## Use
1) Create a bot
2) Update bot token / API in the ENV variable via docker 
3) Submit order to the bot as per the following format: sell BTCUSDT sl=6000 tp=4500 q=10%
        
  
