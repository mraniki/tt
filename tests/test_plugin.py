import pytest
# from unittest.mock import patch, MagicMock
from tt.config import PluginManager

@pytest.mark.asyncio
async def test_load_plugins():
    plugin_manager = PluginManager()
    plugin_manager.load_plugins("tt.plugins")
    await plugin_manager.start_plugin("TalkyTrendPlugin")
    assert len(plugin_manager.plugins) == 1
