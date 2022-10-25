# Telegram Trader
 CCXT and Telegram integration. Based on python telegram bot v20. 
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
 - Disable or Enable trading process via /trading command
 - Query balance via /bal command
 - View opened orders via /order command
 
<img width="393" alt="Screenshot 2022-10-25 at 14 44 41" src="https://user-images.githubusercontent.com/8766259/197776314-10219d7f-693f-44df-8efe-a5794bbafe98.png">

 ## toDo
- formating/handling of response from exchange (bal, opened order, new order)
- formating/handling of error from bot and from exchange api
- handle 2/multi exchanges
- Merge with MQL4 version which integrate with MT4 exchanges (reach out if you are interested)

