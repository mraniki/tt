.. _talky_index:

===========
TalkyTrader
===========

.. image:: ../docs/_static/logo-full.png
  :width: 200
  :alt: logo
  :align: right

| Connect CEX and DEX exchanges across multi messaging platforms.
| Place order, inquire your balance and more through plugins.
| Easily deploy via Docker on self-hosted platform or Paas.

.. raw:: html

   <br>
   <p align="left">
   <a href="https://hub.docker.com/r/mraniki/tt"><img src="https://img.shields.io/docker/pulls/mraniki/tt?style=for-the-badge"></a><br>
   </p>

.. image:: ../docs/_static/screenshot.png
  :width: 200
  :alt: logo
  :align: right


.. warning::

   This is an education tool and should not be considered professional financial investment system nor financial advice.

   Do Your Own Research (DYOR).

   Past performance does not guarantee future results.


.. note::

   * **What is the rationale for building TalkyTrader?**

    * Create an open source platform to allow trading on DEX and CEX on any messaging platform and empower trader with trading tools regardless of the instrument type. Key focus on DEX capability as priority.

    * "so happy I spent $200 on trading signals" said no trader ever. This is a tool to enable traders. This is not a signal platform and not a trading strategy tool. Assumption is you have a `strategy <https://www.investopedia.com/beginner-trading-strategies-4689644>`_.

   * **Aren't there already projects that do this?**

    * Project available usually focused on a given messaging platform (e.g. telegram), a given type of exchange (usually binance), a given type of trading (snipping DEX https://github.com/Nafidinara/bot-pancakeswap or CEX) or full suite trading with CEX focus (https://github.com/Drakkar-Software/OctoBot, https://github.com/freqtrade/freqtrade https://github.com/hummingbot/hummingbot).


User Guide
==========

.. toctree::
   :maxdepth: 2

   01_start
   02_config


Plugins Reference
================

.. toctree::
   :maxdepth: 3

   04_iamlistening
   05_findmyorder
   plugins/helper
   plugins/dex
   plugins/cex
   plugins/talkytrend
   plugins/myllm


TalkyTrader Module
==================

.. toctree::
   :maxdepth: 3

   03_module


Development Reference
=====================

.. toctree::
   :maxdepth: 3

   development/index


.. raw:: html

    <br>
