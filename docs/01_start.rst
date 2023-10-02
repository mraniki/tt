
==================
👋 Getting Started
==================

🐤 Start
========

:doc:`talky:00_base`


💨 Quick Setup
==============

.. note:: First time, use a testnet account and create a sandbox account on Binance https://testnet.binance.org/.
   You can copy/paste the below for quick start using discord platform. You will need to replace the values with your own.
   You might need to add test tokens in your dex wallet via https://faucetlink.to/goerli

   Copy the content to :file:`settings.toml`


   .. code:: toml
   
   # TELEGRAM BOT on CEX Binance
    [default.platform.main]
    bot_token = '121212121'
    bot_channel_id = '-1122121'
    bot_api_id = '1212912'
    bot_api_hash = '121212121' 
    apprise_url = 'tgram:/121221/-11211212121'
    [default.cex.binance]
    name ="binance"
    api_key= ''
    secret = ''
    password = ""
    testmode = true
    defaulttype = "spot"
    ordertype = "market"
    trading_risk_percentage = true
    trading_risk_amount = 1
    trading_slippage = 2
    trading_asset = "USDT"
    trading_asset_separator = ""
    mapping = [
    { id = "BTC", alt = "BTCUSDT" },
    ]



💬 Chat Platform Credentials
=============================

Create your channel/room and your platform bot:

:doc:`iamlistening:index`


💱 Exchange Credentials
=======================

Get your DEX or CEX credentials:

- DEX wallet address and private key: :doc:`talky:plugins/dex`

- CEX API Keys: :doc:`talky:plugins/cex`


⚙️ Setup your config
====================

Create your config file settings.toml or use env variables.
Refer to  :doc:`talky:02_config` for details.

.. warning::

   Use a testnet account or USE AT YOUR OWN RISK. Never share your private keys or API secrets.

   Never use your main account for automatic trade.


.. literalinclude:: ../examples/example_settings.toml


🚀 Deployment
==============

There are two ways you can run TalkyTrader in a production environment. The recommended method is using docker. We also support a traditional deployment method without docker. Read below to see how to get each method set up.

🐳 Docker
---------

.. code:: console

   docker pull mraniki/tt:latest
or

.. code:: console

   docker pull ghcr.io/mraniki/tt:latest


🏠 Local
--------

.. code:: console

   git clone https://github.com/mraniki/tt:main
   pip install -r .requirements/requirements.txt

then start your bot:

.. code:: console

   python3 app.py


☁️ Deploy to cloud services
==========================

.. raw:: html

   <br>
   <a href="https://app.koyeb.com/deploy?type=docker&image=docker.io/mraniki/tt&name=tt-demo"><img src="https://img.shields.io/badge/Deploy%20on%20Koyeb-blue?style=for-the-badge&logo=koyeb"></a>
   <br><br>
   <a href="https://railway.app/new/template/ZVM0QG?referralCode=gxeoRu"><img src="https://img.shields.io/badge/Deploy%20on%20RailWay-black?style=for-the-badge&logo=Railway">

   <br>

