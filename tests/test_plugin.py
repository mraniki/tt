import pytest
from types import ModuleType
import unittest.mock as mock
from talky.config import PluginManager, Plugin


class MockPlugin(Plugin):
    is_plugin = True

    def process(self, message):
        pass
    def start(self):
        pass
    def stop(self):
        pass

@pytest.fixture
def mock_plugin():
    return MockPlugin()

@pytest.fixture
def mock_package(mock_plugin):
    class MockPackage(ModuleType):
        mock_plugin = mock_plugin

        @staticmethod
        def __getattr__(name):
            if name == "mock_plugin":
                return mock_plugin
            raise AttributeError(f"module {__name__} has no attribute {name}")
    return MockPackage

class TestPluginManager:
    def test_load_plugins(self):
        # Create a PluginManager instance
        plugin_manager = PluginManager()
        plugin_manager.plugins = {}

        # Load plugins from the talky.plugins package
        plugin_manager.load_plugins("talky.plugins")

        # Load plugins from the tests package
        # plugin_manager.load_plugins("tests")

        # Check that the plugin was loaded correctly
        assert len(plugin_manager.plugins) == 1

