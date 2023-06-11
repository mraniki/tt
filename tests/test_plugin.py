from types import ModuleType
from unittest.mock import MagicMock
import pytest

from talky.config import PluginManager

class MockPlugin:
    is_plugin = True

    def start(self):
        pass

    def stop(self):
        pass

class MockPackage(ModuleType):
    mock_plugin = MockPlugin()

    @staticmethod
    def __getattr__(name):
        if name == "mock_plugin":
            return MockPlugin()
        raise AttributeError(f"module {__name__} has no attribute {name}")

class TestPluginManager:
    @pytest.fixture
    def plugin_manager(self):
        return PluginManager()

    def test_load_plugins(self, plugin_manager):
        # Mock the importlib and pkgutil modules
        importlib_mock = MagicMock()
        pkgutil_mock = MagicMock()
        importlib_mock.import_module.return_value = pkgutil_mock
        pkgutil_mock.iter_modules.return_value = [(None, "mock_package", None)]
        mock_module = MagicMock()
        mock_module.__name__ = "mock_package"
        mock_module.mock_plugin = MockPlugin()
        mock_package = MagicMock()
        mock_package.mock_plugin = MockPlugin()
        pkgutil_mock.import_module.return_value = mock_package
        plugin_manager.plugins = {}
        plugin_manager._importlib = importlib_mock
        plugin_manager._pkgutil = pkgutil_mock

        # Load plugins from the mock_package package
        plugin_manager.load_plugins("talky.plugins")

        # Check that the plugin was loaded correctly
        assert len(plugin_manager.plugins) == 1
        assert "mock_plugin" in plugin_manager.plugins


    def test_start_plugin(self, plugin_manager):
        # Mock the plugin and start method
        mock_plugin = MagicMock()
        plugin_manager.plugins = {"mock_plugin": mock_plugin}

        # Start the mock plugin
        plugin_manager.start_plugin("mock_plugin")

        # Check that the plugin was started correctly
        mock_plugin.start.assert_called_once()


    def test_stop_plugin(self, plugin_manager):
        # Mock the plugin and stop method
        mock_plugin = MagicMock()
        plugin_manager.plugins = {"mock_plugin": mock_plugin}

        # Stop the mock plugin
        plugin_manager.stop_plugin("mock_plugin")

        # Check that the plugin was stopped correctly
        mock_plugin.stop.assert_called_once()
