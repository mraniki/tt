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

if os.getenv("OP_SERVICE_ACCOUNT_TOKEN"):
    op_path = os.getenv("OP_PATH")
    if not os.path.exists(op_path):
        raise FileNotFoundError(f"OP path '{op_path}' does not exist")
    loguru_logger.debug("Using OnePassword")
    command = [
        op_path,
        "read",
        f"op://{os.getenv('OP_VAULT')}/{os.getenv('OP_ITEM')}/notesPlain",
    ]
    filepath = "/app/tt/settings.toml"
    with open(filepath, "w") as output_file:
        subprocess.run(command, stdout=output_file)


else:
    loguru_logger.debug("No OP service account found")


#######################################
###           ⚙️ Settings           ###
#######################################

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    load_dotenv=True,
    settings_files=[
        # load talky default
        os.path.join(ROOT, "talky_settings.toml"),
        # load default from library in case not in talky default
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

scheduler = AsyncIOScheduler()


########################################
###           🧐 Logging             ###
########################################


class InterceptHandler(logging.Handler):
    def emit(self, record):
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
    loguru_logger.remove()
    # log.configure(**config)
    log_filters = {
        "discord": "ERROR",
        "telethon": "ERROR",
        "web3": "ERROR",
        # "apprise": "ERROR",
        "urllib3": "ERROR",
        # "asyncz": "ERROR",
    }
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    loguru_logger.add(
        sink=sys.stdout,
        level=settings.loglevel,
        filter=log_filters,
    )

    return loguru_logger


logger = loguru_setup()
