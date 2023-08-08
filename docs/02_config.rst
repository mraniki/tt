
======
Config
======

.. toctree::
   :maxdepth: 3

   02_config


Dynaconf
========

Dynaconf https://www.dynaconf.com/ is a powerful and easy-to-use configuration management library for Python.
Talky settings are based on Dynaconf. it support toml settings file, .env file or environment variable 
Refer to Dynaconf for more information.

Settings Structure
==================

Config will load:
    - talky default: talky_settings.toml
    - default from library if the library support it: default_settings.toml
    - user settings: settings.toml
    - user secrets: .secrets.toml

Your settings should be setup in settings.toml, .secrets.toml, .env or environment variable.
    Settings.toml or .env can be located in :file:`/app/settings.toml` or :file:`/app/.env` for docker.
    If deployed locally, place your file in :file:`/tt/` folder.


Talky Settings
==============

More than 100 settings customizable via settings.toml or .env


.. literalinclude:: ../tt/talky_settings.toml
   :linenos:


Settings Example
================

Settings.toml
-------------

.. literalinclude:: ../examples/example_settings.toml
   :linenos:


.env or ENV VARS
------------------

.. literalinclude:: ../examples/example.env
   :linenos:

