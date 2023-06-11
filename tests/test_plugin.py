from unittest.mock import MagicMock
import pytest

from talky.config import settings, logger, PluginManager
from unittest.mock import MagicMock
import pytest

from talky.config import settings, logger, PluginManager

class TestPluginManager:
    @pytest.fixture
    def plugin_manager(self):
        return PluginManager()

    @pytest.fixture
    def mock_plugin(self):
        plugin = MagicMock()
        plugin.is_plugin = True
        return plugin

    def test_load_plugins(self, plugin_manager, mock_plugin):
        # Mock the importlib and pkgutil modules
        importlib_mock = MagicMock()
        pkgutil_mock = MagicMock()
        importlib_mock.import_module.return_value = pkgutil_mock
        pkgutil_mock.iter_modules.return_value = [(None, "mock_plugin", None)]
        mock_module = MagicMock()
        mock_module.__name__ = "mock_plugin"
        mock_module.mock_plugin = mock_plugin
        pkgutil_mock.import_module.return_value = mock_module
        plugin_manager.plugins = {}
        plugin_manager._importlib = importlib_mock
        plugin_manager._pkgutil = pkgutil_mock

        # Load plugins from the mock package
        plugin_manager.load_plugins("mock_package")

        # Check that the plugin was loaded correctly
        assert len(plugin_manager.plugins) == 1
        assert "mock_plugin" in plugin_manager.plugins

    def test_start_plugin(self, plugin_manager, mock_plugin):
        # Mock the plugin and start method
        mock_plugin.start.return_value = None
        plugin_manager.plugins = {"mock_plugin": mock_plugin}

        # Start the mock plugin
        plugin_manager.start_plugin("mock_plugin")

        # Check that the plugin was started correctly
        mock_plugin.start.assert_called_once()

    def test_stop_plugin(self, plugin_manager, mock_plugin):
        # Mock the plugin and stop method
        mock_plugin.stop.return_value = None
        plugin_manager.plugins = {"mock_plugin": mock_plugin}

        # Stop the mock plugin
        plugin_manager.stop_plugin("mock_plugin")

        # Check that the plugin was stopped correctly
        mock_plugin.stop.assert_called_once()
