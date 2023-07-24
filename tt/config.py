"""
 talky  Config
 Used to define 
 dynaconf setting import, 
 logging setup and 
 scheduler

"""
import logging
import os

from asyncz.schedulers.asyncio import AsyncIOScheduler
from dynaconf import Dynaconf

# from loguru import logger

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=settings.loglevel
)

logger = logging.getLogger("TalkyTrader")

if settings.loglevel == "DEBUG":
    logging.getLogger("discord").setLevel(logging.ERROR)
    logging.getLogger("telethon").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("apprise").setLevel(logging.ERROR)
    logging.getLogger("web3").setLevel(logging.ERROR)


# def configure_logger() -> None:
#     logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=settings.loglevel
#     )
#     logger = logging.getLogger("TalkyTrader")
#     # logger.remove()
#     # logger.add(
#     #     sys.stderr,
#     #     level=settings.loglevel or "INFO",
#     #     colorize=True,
#     #     format="<level>{message}</level>",
#     # )
#     logging.getLogger("discord").setLevel(logging.INFO)
#     logging.getLogger("telethon").setLevel(logging.INFO)
#     logging.getLogger("urllib3").setLevel(logging.INFO)
#     logging.getLogger("apprise").setLevel(logging.INFO)
#     logging.getLogger("web3").setLevel(logging.INFO)

# logger = configure_logger()

########################################
###          ⏱️ Scheduling           ###
########################################

scheduler = AsyncIOScheduler()

