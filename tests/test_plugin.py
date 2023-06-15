import pytest
from tt.utils import MessageProcessor

@pytest.mark.asyncio
async def test_load_plugins():
    plugin_manager = MessageProcessor()
    plugin_manager.load_plugins("tt.plugins")

    print("Loaded plugins:", plugin_manager.plugins)

    assert len(plugin_manager.plugins) == 1
