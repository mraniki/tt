import asyncio
import importlib
import os
import pkgutil
import logging
from dynaconf import Dynaconf

ROOT = os.path.dirname(__file__)

settings = Dynaconf(
    envvar_prefix="TT",
    root_path=os.path.dirname(ROOT),
    load_dotenv=True,
    settings_files=[
        os.path.join(ROOT, "default_settings.toml"),
        'settings.toml',
        '.secrets.toml'
        ],
    environments=True,
    merge=True,
    default_env="default",
)


#  🧐LOGGING
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=settings.loglevel
)
logger = logging.getLogger("TalkyTrader")
if settings.loglevel == "DEBUG":
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    #logging.getLogger("ccxt").setLevel(logging.WARNING)

# class PluginManager:
#     def __init__(self):
#         self.plugins = []

#     def load_plugin(self, plugin_name):
#         try:
#             module = importlib.import_module(plugin_name)
#             plugin = module.Plugin()
#             self.plugins.append(plugin)
#             logger.info(f"Plugin '{plugin_name}' loaded successfully")
#         except Exception as e:
#             logger.error(f"Failed to load plugin '{plugin_name}': {e}")

#     async def start_plugins(self):
#         event_loop = asyncio.get_event_loop()
#         for plugin in self.plugins:
#             event_loop.create_task(plugin.start())

#     async def stop_plugins(self):
#         event_loop = asyncio.get_event_loop()
#         for plugin in self.plugins:
#             event_loop.create_task(plugin.stop())
