
======
Config
======

Dynaconf
========

Dynaconf https://www.dynaconf.com/ is a powerful and easy-to-use configuration management library for Python.
Talky settings are based on Dynaconf.


Settings  Structure
===================

Config will load:
    - load talky default: talky_settings.toml
    - load default from library: default_settings.toml
    - load user settings: settings.toml
    - load user secrets: .secrets.toml

Your settings should be setup in settings.toml or .secrets.toml
Settings.toml or .env can be located in /app/settings.toml or /app/.env for docker.
If deployed locally, place your settings.toml or .env in /tt.


Talky Settings
==============

 More than 100 settings customizable via settings.toml or .env


.. literalinclude:: ../tt/talky_settings.toml
   :linenos:


Settings Example
================

Settings.toml
-------------
example:

.. literalinclude:: ../examples/example_settings.toml

.env or ENV VARS
------------------

place the .env at

.. literalinclude:: ../examples/example.env
