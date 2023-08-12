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
   <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"><br>
    <a href="https://hub.docker.com/r/mraniki/tt"><img src="https://img.shields.io/docker/pulls/mraniki/tt?style=for-the-badge"></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge"></a>
    <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/linter-ruff-261230.svg?style=for-the-badge"></a>
    <a href="https://semver.org"><img src="https://img.shields.io/badge/release-semantic-e10079.svg?style=for-the-badge"></a>


   <br>
   </p>

|

.. image:: ../docs/_static/screenshot.png
  :width: 200
  :alt: logo
  :align: right


.. note::

    What is the rationale for building TalkyTrader?
    - create an open source platform to allow trading on DEX and CEX on any type of messaging platform
    - "so happy I spent $200 on trading signals" said no trader ever.

    Aren't there already projects that do this?
    - project available usually focused on a given messaging platform (eg telegram), a given type of exchange (usually CeX binance) or given type of trading (snipping DEX shitcoin, scalping CEX).

.. warning::

   This is an education tool and should not be considered professional financial investment system nor financial advice.

   Use a testnet account or USE AT YOUR OWN RISK. Never share your private keys or API secrets.

   Never use your main account for automatic trade.

   DYOR.


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

    <br><br>
