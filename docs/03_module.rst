===========
TalkyTrader
===========

.. automodule:: tt.bot
    :members:
    :undoc-members:
    

API EndPoint
============

Talky Trader is an app built with FastAPI https://fastapi.tiangolo.com
It allows you to connect to a messaging chat platform to interact with
trading module.

HealthCheck
-----------

End point to know if the API is up and running

.. autofunction::tt.bot.health_check

Webhook
-------

Webhook endpoint to send your trade generated via http://tradingview.com 
or anyother platform you work with.
Endpoint is :file:`/webhook/{settings.webhook_secret}` so in trading view you can add:
https://talky.trader.com/webhook/123456

.. autofunction::tt.bot.webhook

Startup
-------

Starting the coroutine run_bot

.. autofunction::tt.bot.start_bot_task


iamlistening
============

:doc:`iamlistening:index`


FindMyOrder
===========

:doc:`findmyorder:index`

Plugins
=======

Plugins are the core of Talky Trader, they are loaded at startup and
are used to interact with the trading platform.


.. automodule:: tt.plugins
    :members:
    :undoc-members:


TalkyTrader Module Reference
=====================

.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   tt
   
  
   
