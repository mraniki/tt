import pytest
from tt.utils import PluginManager

@pytest.mark.asyncio
async def test_load_plugins():
    plugin_manager = PluginManager()
    plugin_manager.load_plugins("tt.plugins")

    print("Loaded plugins:", plugin_manager.plugins)

    for plugin_name, plugin_instance in plugin_manager.plugins.items():
        print("Plugin:", plugin_name)
        print("Plugin instance:", plugin_instance)

        await plugin_instance.start()

    assert len(plugin_manager.plugins) == 1
