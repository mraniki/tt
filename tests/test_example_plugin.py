import pytest
import importlib
from unittest.mock import AsyncMock
from tt.config import settings
from tt.plugins.plugin_manager import PluginManager
from tt.plugins.default_plugins.example_plugin import ExamplePlugin

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin_manager")
def message_processor_fixture():
    plugin_manager = PluginManager()
    plugin_manager.load_plugins()
    return plugin_manager


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return ExamplePlugin()

@pytest.mark.asyncio
async def test_plugin_manager():
    plugin_manager = PluginManager()
    assert plugin_manager is not None

@pytest.mark.asyncio
async def test_load_one_plugin():
    plugin_module = importlib.import_module(
        'tt.plugins.default_plugins.example_plugin')
    plugin_manager = PluginManager()
    assert plugin_manager is not None
    plugin_manager.load_plugin(plugin_module,'example_plugin')
    assert plugin_manager.plugins is not None
    assert len(plugin_manager.plugins) >= 1
    assert isinstance(plugin_manager.plugins[0], ExamplePlugin)

@pytest.mark.asyncio
async def test_load_plugins(caplog):
    settings.talkytrend_enabled = False
    plugin_manager = PluginManager()
    print(plugin_manager)
    assert plugin_manager is not None
    plugin_manager.load_plugins()
    print(plugin_manager.plugins)
    assert plugin_manager.plugins is not None
    await plugin_manager.start_all_plugins()
    assert 'Loading plugins from' in caplog.text

@pytest.mark.asyncio
async def test_start_plugin(caplog):
    plugin_module = importlib.import_module(
        'tt.plugins.default_plugins.example_plugin')
    plugin_manager = PluginManager()
    print(plugin_manager)
    assert plugin_manager is not None
    plugin_manager.load_plugin(plugin_module,'example_plugin')
    example_plugin = ExamplePlugin()
    await plugin_manager.start_plugin(example_plugin)
    print(caplog.text)
    assert 'plugin started' in caplog.text
    assert 'plugin enabled' in caplog.text

@pytest.mark.asyncio
async def test_plugin(plugin, plugin_manager):
    handle_message = AsyncMock()
    await plugin_manager.process_message(
        f"{settings.bot_prefix}{settings.bot_command_help}")
    assert plugin.should_handle("any message") is True
    handle_message.assert_awaited_once

@pytest.mark.asyncio
async def test_plugin_notification(plugin, plugin_manager):
    """Test notification """
    send_notification = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    send_notification.assert_awaited_once

