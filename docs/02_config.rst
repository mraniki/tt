
==========
⚙️ Config
==========

.. toctree::
   :maxdepth: 3

   02_config


Dynaconf
========

.. image:: https://img.shields.io/badge/⚙️dynaconf-005571?style=for-the-badge&logo=settings&logoColor=ffdd54
  :align: right


Dynaconf is a powerful and easy-to-use configuration management library for Python.
Talky settings are based on Dynaconf. It supports TOML settings file, .env file or environment variable , and other types.
Refer to https://github.com/dynaconf/dynaconf for more information.


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

1Password
=========

In case, you use 1Password to store your settings, you can use :file:`.secrets.toml` to retrieve and store your settings from a notesPlain item.
in order to use 1Password, you need to add the following to your :file:`.env` file:
    - OP_SERVICE_ACCOUNT_TOKEN: your 1Password service account token
    - OP_VAULT: your 1Password vault
    - OP_ITEM: your 1Password item
    - OP_PATH: your one 1Password path (optional and default value `/usr/bin/op`)

The :file:`.secrets.toml` will be located in :file:`/tt/.secrets.toml` and  be created by the OP client via `op read op://vault/item/notesPlain > .secrets.toml`


Talky Settings
==============

More than 100 settings customizable via settings.toml or .env.
Most of them are predefined and you only need to update the credentials realted to your exchange and chat platform


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


Config 
=======

.. automodule:: tt.config
    :members:
    :undoc-members:
