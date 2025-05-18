"""
TalkyTrader Settings, Scheduling and Logging,
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
    If you use 1Password to store your settings,
    you can use :file:`.secrets.toml` to retrieve and
    store your settings from a notesPlain item.
    more info: https://support.1password.com/command-line-getting-started/

    You need the following to your :file:`.env` file:
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

    # Use TT_CONFIG_DIR if available, otherwise use app directory
    config_dir = os.getenv("TT_CONFIG_DIR", "/app")

    # Create both settings.toml and .op.toml for maximum compatibility
    op_filepath = os.path.join(config_dir, "settings.toml")

    try:
        loguru_logger.debug(f"Writing 1Password settings to {op_filepath}")
        with open(op_filepath, "w") as output_file:
            subprocess.run(command, stdout=output_file, check=True)

        # Also create .op.toml as a symlink or copy for backward compatibility
        op_backup = os.path.join(config_dir, ".op.toml")
        if os.path.exists(op_filepath):
            loguru_logger.debug(f"Creating backup at {op_backup}")
            with open(op_filepath, "r") as src, open(op_backup, "w") as dst:
                dst.write(src.read())
    except Exception as e:
        loguru_logger.error(f"Error writing 1Password settings: {e}")
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


# Get config directory from environment or use a default
config_dir = os.getenv("TT_CONFIG_DIR", os.path.dirname(ROOT))
loguru_logger.debug(f"Config directory: {config_dir}")

# Define possible locations for settings files
settings_locations = [
    # Current directory and config directory for relative paths
    ".",
    config_dir,
    # App directory if different
    "/app",
    # tt subdirectory
    os.path.join(config_dir, "tt"),
]

# Build complete list of settings files to try
settings_files = [
    # Always include talky default settings first
    os.path.join(ROOT, "talky_settings.toml"),
]

# Add other settings files with potential paths
for location in settings_locations:
    for filename in (
        "default_settings.toml",
        "settings.toml",
        ".secrets.toml",
        ".op.toml",
    ):
        potential_path = os.path.join(location, filename)
        if os.path.isfile(potential_path):
            loguru_logger.debug(f"Found settings file: {potential_path}")
            settings_files.append(potential_path)

# Ensure logging of settings loaded
loguru_logger.debug(f"Settings files to be loaded: {settings_files}")

# Load the settings using Dynaconf
settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    load_dotenv=True,
    settings_files=settings_files,
    environments=True,
    merge_enabled=True,  # Ensure merging is enabled
    default_env="default",
)

# Log the loaded settings for verification
loguru_logger.debug(f"Loaded settings: {settings.to_dict()}")


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
        "yfinance": settings.thirdparty_lib_loglevel,
        "peewee": settings.thirdparty_lib_loglevel,
        "httpx": settings.thirdparty_lib_loglevel,
        "openai": settings.thirdparty_lib_loglevel,
        "httpcore": settings.thirdparty_lib_loglevel,
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
