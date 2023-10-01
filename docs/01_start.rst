
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

      [default]
      bot_token = 'your_discord_bot_token'
      bot_channel_id = 'your_discord_channel_id'
      apprise_url = 'discord://your_discord_webhookid/your_discord_webhooktoken'
      dex_rpc = "https://rpc.ankr.com/eth_goerli"
      dex_wallet_address = '0xyour_private_key'
      dex_private_key = '0xyour_private_key'
      dex_block_explorer_url = "https://api-goerli.etherscan.io/"
      dex_block_explorer_api = "your_blockscan_api_key"
      trading_asset_address = "0xa3726f2e6423caF1824cD7721B543B29b621fB4f"
      cex_enabled = true
      cex_name = 'binance'
      cex_api = 'your_binance_api_sandbox_key'
      cex_secret = 'your_binance_api_sandbox_secret'
      cex_testmode = true
      cex_defaulttype = "spot"
      cex_ordertype = "market"


   or use the following for your .env or env variables:

   .. code:: console

      TT_BOT_TOKEN = 'your_discord_bot_token'
      TT_BOT_CHANNEL_ID = 'your_discord_channel_id'
      TT_APPRISE_URL = 'discord://your_discord_webhookid/your_discord_webhooktoken'
      TT_DEX_RPC = "https://rpc.ankr.com/eth_goerli"
      TT_DEX_WALLET_ADDRESS = '0xyour_wallet_address'
      TT_DEX_PRIVATE_KEY = '0xyour_private_key'
      TT_DEX_BLOCK_EXPLORER_URL = "https://api-goerli.etherscan.io/"
      TT_DEX_BLOCK_EXPLORER_API = "your_blockscan_api_key"
      TT_TRADING_ASSET_ADDRESS = "0xa3726f2e6423caF1824cD7721B543B29b621fB4f"
      TT_CEX_ENABLED = true
      TT_CEX_NAME = 'binance'
      TT_CEX_API = 'your_binance_api_sandbox_key'
      TT_CEX_SECRET = 'your_binance_api_sandbox_secret'
      TT_CEX_TESTMODE = true
      TT_CEX_DEFAULTTYPE = "spot"
      TT_CEX_ORDERTYPE = "market"



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

