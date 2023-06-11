
import os
import logging
from dynaconf import Dynaconf

import importlib
import pkgutil

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
        print(f"Loading plugins from package: {package_name}")
        package = importlib.import_module(package_name)
        print(f"Package loaded: {package}")

        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{plugin_name}")
                if plugin_class := next(
                    (
                        obj
                        for name, obj in module.__dict__.items()
                        if isinstance(obj, type)
                        and issubclass(obj, BasePlugin)
                        and obj is not BasePlugin
                    ),
                    None,
                ):
                    plugin_instance = plugin_class()
                    self.plugins[plugin_name] = plugin_instance
                    print(f"Plugin loaded: {plugin_name}")
                else:
                    print(f"No plugin class found in module: {plugin_name}")

            except Exception as e:
                print(f"Error loading plugin: {plugin_name}, {e}")

    async def start_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]
            await plugin_instance.start()
        else:
            print(f"Plugin not found: {plugin_name}")

class BasePlugin:
    def start(self):
        pass

    def stop(self):
        pass

    async def listen(self):
        pass

    async def notify(self, message):
        pass
