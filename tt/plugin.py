# remove this line: from tt.plugin import register_plugin, Plugin
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @abstractmethod
    def process_message(self, message):
        pass

# define your Plugin class to inherit from BasePlugin
class Plugin(BasePlugin):
    def __init__(self, name):
        self.name = name

    def start(self):
        pass

    def stop(self):
        pass


_plugins = {}


def register_plugin(cls):
    _plugins[cls.__name__] = cls
    return cls