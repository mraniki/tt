

from abc import ABC, abstractmethod
import importlib
import pkgutil


class BasePlugin(ABC):
    @abstractmethod
    def process(self, input):
        pass


_plugins = {}


def register_plugin(cls):
    _plugins[cls.__name__] = cls
    return cls


class PluginManager:
    def __init__(self):
        self.plugins = {}
        self._importlib = importlib
        self._pkgutil = pkgutil

    @property
    def pkgutil(self):
        return self._pkgutil

    def load_plugins(self, package_name):
        print(f"Loading plugins from package: {package_name}")
        package = importlib.import_module(package_name)
        print(f"Package loaded: {package}")
        for _, plugin_name, _ in self._pkgutil.iter_modules(package.__path__):
            try:
                module = importlib.import_module(f"{package_name}.{plugin_name}")
                plugin_class = getattr(module, plugin_name)
                if issubclass(plugin_class, BasePlugin) and plugin_class is not BasePlugin:
                    self.plugins[plugin_name] = plugin_class
                    print(f"Plugin loaded: {plugin_name}")
            except Exception as e:
                print(f"Error loading plugin: {plugin_name}, {e}")

    async def start_plugin(self, plugin_name):
        if plugin := self.plugins.get(plugin_name):
            await plugin.start()
        else:
            print(f"Plugin {plugin_name} not found.")

    async def stop_plugin(self, plugin_name):
        if plugin := self.plugins.get(plugin_name):
            await plugin.stop()
        else:
            print(f"Plugin {plugin_name} not found.")
