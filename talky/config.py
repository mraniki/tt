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


class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self, package_name):
        package = importlib.import_module(package_name)
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            module = importlib.import_module(f"{package_name}.{name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "is_plugin") and attr.is_plugin:
                    self.plugins[attr_name] = attr()

    async def start_plugin(self, plugin_name):
        plugin = self.plugins.get(plugin_name)
        if plugin:
            await plugin.start()
        else:
            print(f"Plugin {plugin_name} not found.")

    async def stop_plugin(self, plugin_name):
        plugin = self.plugins.get(plugin_name)
        if plugin:
            await plugin.stop()
        else:
            print(f"Plugin {plugin_name} not found.")

