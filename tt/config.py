"""
 talky  Config
"""
import logging
import os

from asyncz.schedulers.asyncio import AsyncIOScheduler  # noqa: F401
from dynaconf import Dynaconf

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


#  🧐LOGGING
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




# # Define the scheduler
# scheduler = AsyncIOScheduler(
#     {
#         "asyncz.stores.mongo": {"type": "mongodb"},
#         "asyncz.stores.default": {"type": "redis", "database": "0"},
#         "asyncz.executors.threadpool": {
#             "max_workers": "20",
#             "class": "asyncz.executors.threadpool:ThreadPoolExecutor",
#         },
#         "asyncz.executors.default": {
# "class": "asyncz.executors.asyncio::AsyncIOExecutor"},
#         "asyncz.task_defaults.coalesce": "false",
#         "asyncz.task_defaults.max_instances": "3",
#         "asyncz.task_defaults.timezone": "UTC",
#     },
# )