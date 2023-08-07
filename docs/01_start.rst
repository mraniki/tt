
===============
Getting Started
===============

Chat Platform Credentials
=========================

Create your channel/room and your platform bot:

:doc:`iamlistening:index`


Exchange Credentials
====================

Get your DEX or CEX credentials:
- DEX wallet address and private key: :doc:`talky:plugins/dex`
- CEX API Keys: :doc:`talky:plugins/cex`

Setup your config
=================

Create your config file settings.toml or use env variables. 
Refer to  :doc:`talky:02_config` for details.

example:

.. literalinclude:: ../examples/example_settings.toml


Deployment
==========

Docker Deployment
-----------------

.. code:: console

   docker pull mraniki/tt:latest
or

.. code:: console

   docker pull ghcr.io/mraniki/tt:latest


Local Deployment
-----------------

.. code:: console
   
   git clone https://github.com/mraniki/tt:main
   pip install -r .requirements/requirements.txt

then start your bot:

.. code:: console

   python3 bot.py


.. raw:: html

   <br>
