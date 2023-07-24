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
from loguru import logger as log

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

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=settings.loglevel
# )

# logger = logging.getLogger("TalkyTrader")


def loguru_setup():
    log.remove()
    # log.configure(**config)
    log.add(
        sink=sys.stdout,
        level=settings.loglevel,
    )

    return log

logger = loguru_setup()

if settings.loglevel == "DEBUG":
    logging.getLogger("discord").setLevel(logging.ERROR)
    logging.getLogger("telethon").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("apprise").setLevel(logging.ERROR)
    logging.getLogger("web3").setLevel(logging.ERROR)

########################################
###          ⏱️ Scheduling           ###
########################################

scheduler = AsyncIOScheduler()

