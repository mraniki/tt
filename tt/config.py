"""
TalkyTrader Config
Used for Logging,
Scheduleing and Settings
    🧐⏱️⚙️

"""

import logging
import os
import subprocess
import sys

import dotenv
from asyncz.schedulers.asyncio import AsyncIOScheduler
from dynaconf import Dynaconf
from loguru import logger as loguru_logger

dotenv.load_dotenv()
#######################################
###           ㊙️ Secrets            ###
#######################################

"""
    In case, you use 1Password to store your settings, you can use :file:`.secrets.toml` 
    to retrieve and store your settings from a notesPlain item.
    more info: https://support.1password.com/command-line-getting-started/

    in order to use 1Password, you need to add the following to your :file:`.env` file:
    - OP_SERVICE_ACCOUNT_TOKEN: your 1Password service account token
    - OP_VAULT: your 1Password vault
    - OP_ITEM: your 1Password item
    - OP_PATH: your one 1Password path (optional and default value `/usr/bin/op`)

    The :file:`.secrets.toml` will be located in :file:`/tt/.secrets.toml` and 
    be created by the OP client via `op read op://vault/item/notesPlain > .secrets.toml`

"""

if os.getenv("OP_SERVICE_ACCOUNT_TOKEN") and os.path.exists(os.getenv("OP_PATH")):
    loguru_logger.debug("Using OnePassword")
    command = [
        os.getenv("OP_PATH"),
        "read",
        f"op://{os.getenv('OP_VAULT')}/{os.getenv('OP_ITEM')}/notesPlain",
    ]
    filepath = "/app/tt/.op.toml"
    with open(filepath, "w") as output_file:
        subprocess.run(command, stdout=output_file)
else:
    loguru_logger.debug("No OP service account found")


#######################################
###           ⚙️ Settings           ###
#######################################

"""
 Settings are loaded via dynaconf
 Dynaconf is a powerful and easy-to-use 
 management library for Python.
 It supports TOML settings file, .env file or environment variable, and other types.
 Refer to https://github.com/dynaconf/dynaconf for more information.

 More than 100 settings customizable via settings.toml or .env.
 Most of them are predefined and you only need to 
 update the credentials related to your exchange and chat platform

 Config will load:
    - talky default: talky_settings.toml
    - default from library if the library support it: default_settings.toml
    - user settings: settings.toml
    - user secrets: .secrets.toml

 Your settings should be setup in 
 settings.toml, 
 .secrets.toml, 
 .env or 
 environment variable.
 Settings.toml or .env can be located in :file:`/app/settings.toml` 
 or :file:`/app/.env` for docker.
 If deployed locally, place your file in :file:`/tt/` folder.

"""

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    load_dotenv=True,
    settings_files=[
        # load talky default
        os.path.join(ROOT, "talky_settings.toml"),
        # load lib default
        "default_settings.toml",
        # load user default
        "settings.toml",
        # load user secret
        ".secrets.toml",
        # load settings from one password vault
        ".op.toml",
    ],
    environments=True,
    merge_enabled=True,
    default_env="default",
)


########################################
###          ⏱️ Scheduling           ###
########################################

"""
Scheduling is managed via asyncz lib
More info: https://github.com/tarsil/asyncz

It allows you to schedule tasks at plugin level.
Refer to the plugin documentation 
:file:`tt.plugins.plugin_manager`

"""

scheduler = AsyncIOScheduler()


########################################
###           🧐 Logging             ###
########################################

"""
Logging is managed via loguru
"""


class InterceptHandler(logging.Handler):
    """
    InterceptHandler is a loguru handler
    that intercepts all log records.
    It can be used as a replacement for logging.basicConfig()
    """

    def emit(self, record):
        """
        Emit a log record.

        Args:
            record (logging.LogRecord): The log record to emit.

        Returns:
            None
        """
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def loguru_setup():
    """
    Set up the loguru logger with custom configurations.

    Returns:
        loguru.logger: The configured loguru logger instance.
    """
    loguru_logger.remove()
    log_filters = {
        "discord": settings.thirdparty_lib_loglevel,
        "telethon": settings.thirdparty_lib_loglevel,
        "web3": settings.thirdparty_lib_loglevel,
        "apprise": settings.thirdparty_lib_loglevel,
        "urllib3": settings.thirdparty_lib_loglevel,
        "asyncz": settings.thirdparty_lib_loglevel,
        "rlp": settings.thirdparty_lib_loglevel,
        "numexpr": settings.thirdparty_lib_loglevel,
    }
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    loguru_logger.add(
        sink=sys.stdout,
        level=settings.loglevel,
        filter=log_filters,
    )
    if settings.loglevel == "DEBUG":
        loguru_logger.warning(
            """
            DEBUG ENABLED, 
            You can disable it 
            loglevel='INFO' in settings.toml
            TT_LOGLEVEL=INFO in your .env or vars.
            """
        )
    return loguru_logger


logger = loguru_setup()
