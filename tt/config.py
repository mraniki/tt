
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
                plugin_class = getattr(module, plugin_name)
                if issubclass(plugin_class, BasePlugin) and plugin_class is not BasePlugin:
                    self.plugins[plugin_name] = plugin_class()
                    print(f"Plugin loaded: {plugin_name}")
            except Exception as e:
                print(f"Error loading plugin: {plugin_name}, {e}")

    async def start_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            plugin_instance = self.plugins[plugin_name]
            plugin_instance.start()
            await plugin_instance.listen()
        else:
            print(f"Plugin '{plugin_name}' not found.")

class BasePlugin:
    def start(self):
        pass

    def stop(self):
        pass

    async def listen(self):
        pass

    async def notify(self, message):
        pass
