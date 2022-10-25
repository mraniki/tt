# Telegram Trader
Based on python telegram bot v20
Deploy it via docker. 
 
## Install
1) Create a bot via [@BotFather ](https://core.telegram.org/bots/tutorial)
2) Create your API Keys supported by CCXT https://github.com/ccxt/ccxt
3) Update bot token / API in the ENV variable via docker  or git clone and use .env file
4) Submit order to the bot as per the following Order format DIRECTION SYMBOL STOPLOSS TAKEPROFIT QUANTITY 
  (e.g. sell BTCUSDT sl=6000 tp=4500 q=10%) 
 
## ENV Variables:

    #Telegram bot token 
    TOKEN="" 
    #TG user for bot control
    ALLOWED_USER_ID=""
    
    #CCXT supported exchange 
    EXCHANGE1= ""
    #APIKEY
    EXCHANGE1YOUR_API_KEY= ""
    #APISECRET
    EXCHANGE1YOUR_SECRET= "" 
        
 ## Use Case
 - Push your signal manually or from system like  trading view to submit order to your exchange
