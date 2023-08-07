
===============
Getting Started
===============

Chat Platform Credentials
=========================

Create your channel/room and your platform bot:

   :doc:`talky:04_iamlistening`

   :doc:`iamlistening:index`

Exchange Credentials
====================

- DEX wallet address and private key
- CEX API Keys

Setup your config
=================
Create your config file settings.toml or use env variables. 
Refer to 02_config for more details.

Settings.toml
-------------

example:

.. literalinclude:: ../examples/example_settings.toml

.env or ENV VARS
------------------

place the .env at

.. literalinclude:: ../examples/example.env

Deployment
==========

Docker Deployment
-----------------
Settings.toml or .env can be located in /app/settings.toml or /app/.env

.. code:: console

   docker pull mraniki/tt:latest
or

.. code:: console

   docker pull ghcr.io/mraniki/tt:latest


Local Deployment
-----------------
place your settings.toml or .env in /tt

.. code:: console
   
   git clone https://github.com/mraniki/tt:main
   pip install -r .requirements/requirements.txt

then start your bot:

.. code:: console

   python3 bot.py




.. raw:: html

   <br>
