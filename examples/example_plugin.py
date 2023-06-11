
# from YOURPLUGIN import YOURCLASS
from talky.plugin import Plugin, register_plugin
from talky.config import settings

class MyPlugin(Plugin):
    def __init__(self):
        # Initialize your plugin here
        pass

    async def start(self):
        # Start your plugin here
        pass

    async def stop(self):
        # Stop your plugin here
        pass

@register_plugin
class MyPluginWrapper:
    def __init__(self):
        self.plugin = MyPlugin()

    async def start(self):
        await self.plugin.start()

    async def stop(self):
        await self.plugin.stop()
