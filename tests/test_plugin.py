import pytest
from tt.utils import PluginManager

@pytest.mark.asyncio
async def test_load_plugins():
    plugin_manager = PluginManager()
    plugin_manager.load_plugins("tt.plugins")

    print("Loaded plugins:", plugin_manager.plugins)

    assert len(plugin_manager.plugins) == 1
