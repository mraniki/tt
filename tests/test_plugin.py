import pytest
from unittest.mock import patch
from tt.config import PluginManager, BasePlugin

# Sample plugin for testing
class TestPlugin(BasePlugin):
    def start(self):
        pass

    def stop(self):
        pass

    async def listen(self):
        pass

    async def notify(self, message):
        pass

def test_load_plugins():
    plugin_manager = PluginManager()

    # Mocking the package and modules
    mock_package = "tt.plugins"
    mock_module1 = "tt.plugins.plugin1"
    mock_module2 = "tt.plugins.plugin2"

    # Mocking the importlib.import_module function
    with patch("importlib.import_module") as mock_import_module:
        # Mocking the pkgutil.iter_modules function
        with patch("pkgutil.iter_modules") as mock_iter_modules:
            # Set up the mock return values for pkgutil.iter_modules
            mock_iter_modules.return_value = [("", "plugin1", False), ("", "plugin2", False)]

            # Set up the mock return values for importlib.import_module
            mock_import_module.side_effect = [module1, module2]

            # Call the load_plugins method
            plugin_manager.load_plugins(mock_package)

    # Assertions
    assert len(plugin_manager.plugins) == 2
    assert "plugin1" in plugin_manager.plugins
    assert "plugin2" in plugin_manager.plugins

def test_start_plugin():
    plugin_manager = PluginManager()

    # Mocking the plugin instance
    plugin_instance = TestPlugin()
    plugin_manager.plugins["test_plugin"] = plugin_instance

    # Mocking the start and listen methods
    with patch.object(plugin_instance, "start") as mock_start, \
         patch.object(plugin_instance, "listen") as mock_listen:
        
        # Call the start_plugin method
        plugin_manager.start_plugin("test_plugin")

    # Assertions
    mock_start.assert_called_once()
    mock_listen.assert_awaited_once()