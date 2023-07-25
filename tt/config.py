"""
 talky  Config
 Used to define 
 dynaconf setting import, 
 logging setup and 
 scheduler

"""
import logging
import os
import sys

from asyncz.schedulers.asyncio import AsyncIOScheduler
from dynaconf import Dynaconf
from loguru import logger as loguru_logger

########################################
###            ⚙️ Settings            ###
########################################

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    load_dotenv=True,
    settings_files=[
        os.path.join(ROOT, "talky_settings.toml"), #load talky default
        "default_settings.toml",#load plugin/ lib
        'settings.toml', #load user default
        '.secrets.toml'
        ],
    environments=True,
    merge_enabled=True,
    # merge=True,
    default_env="default",
)

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

        logger.opt(
            depth=depth, exception=record.exc_info).log(
                level, record.getMessage())

def loguru_setup():
    loguru_logger.remove()
    # log.configure(**config)
    log_filters = {
    "discord": "INFO",
    "telethon": "INFO",
    "web3": "INFO",
    "apprise": "INFO",
    "urllib3": "INFO",
        }
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    loguru_logger.add(
        sink=sys.stderr,
        level=settings.loglevel,
        filter=log_filters,
    )

    return loguru_logger

logger = loguru_setup()


# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=settings.loglevel
# )
# logger = logging.getLogger("TalkyTrader")
# if settings.loglevel == "DEBUG":
#     logging.getLogger("discord").setLevel(logging.ERROR)
#     logging.getLogger("telethon").setLevel(logging.ERROR)
#     logging.getLogger("urllib3").setLevel(logging.ERROR)
#     logging.getLogger("apprise").setLevel(logging.ERROR)
#     logging.getLogger("web3").setLevel(logging.ERROR)

########################################
###          ⏱️ Scheduling           ###
########################################

scheduler = AsyncIOScheduler()

