import importlib
from unittest.mock import AsyncMock

import pytest
from asyncz.triggers import CronTrigger

from tt.config import settings
from tt.plugins.default_plugins.example_plugin import ExamplePlugin
from tt.plugins.plugin_manager import BasePlugin, PluginManager


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
async def test_baseplugin_class():
    plugin = BasePlugin()
    assert callable(plugin.start)
    assert callable(plugin.stop)
    assert callable(plugin.send_notification)
    assert callable(plugin.should_handle)
    assert callable(plugin.handle_message)
    assert callable(plugin.plugin_notify_cron_task)
    assert callable(plugin.plugin_notify_schedule_task)


@pytest.mark.asyncio
async def test_baseplugin():
    plugin = BasePlugin()
    await plugin.start()
    assert plugin is not None
    await plugin.stop()
    assert plugin is not None


@pytest.mark.asyncio
async def test_load_one_plugin():
    plugin_module = importlib.import_module("tt.plugins.default_plugins.example_plugin")
    plugin_manager = PluginManager()
    assert plugin_manager is not None
    plugin_manager.load_plugin(plugin_module, "example_plugin")
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
    assert "Loading plugins from" in caplog.text


@pytest.mark.asyncio
async def test_start_plugin(caplog):
    plugin_module = importlib.import_module("tt.plugins.default_plugins.example_plugin")
    plugin_manager = PluginManager()
    print(plugin_manager)
    assert plugin_manager is not None
    plugin_manager.load_plugin(plugin_module, "example_plugin")
    example_plugin = ExamplePlugin()
    await plugin_manager.start_plugin(example_plugin)
    print(caplog.text)
    assert "plugin started" in caplog.text
    assert "plugin enabled" in caplog.text


@pytest.mark.asyncio
async def test_plugin_notification(plugin, plugin_manager):
    """Test notification"""
    send_notification = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    send_notification.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_notify_cron_task():
    plugin = BasePlugin()
    plugin.scheduler = AsyncMock()
    plugin.send_notification = AsyncMock()
    function_result = "Test Result"
    function_mock = AsyncMock(return_value=function_result)

    await plugin.plugin_notify_cron_task(
        user_name="Test User",
        user_day_of_week="mon-fri",
        user_hours="6,12,18",
        user_timezone="UTC",
        function=function_mock,
    )

    plugin.scheduler.add_task.assert_called_once_with(
        name="Test User",
        fn=plugin.send_notification,
        args=[function_result],
        trigger=CronTrigger(day_of_week="mon-fri", hour="6,12,18", timezone="UTC"),
        is_enabled=True,
    )


@pytest.mark.asyncio
async def test_plugin_notify_schedule_task():
    plugin = BasePlugin()
    plugin.scheduler = AsyncMock()
    plugin.send_notification = AsyncMock()
    function_result = "Test Result"
    function_mock = AsyncMock(return_value=function_result)
    await plugin.plugin_notify_schedule_task(
        user_name="Test User", frequency=8, function=function_mock
    )

    plugin.scheduler.add_task.assert_awaited_once


@pytest.mark.asyncio
async def test_should_handle_timeframe():
    plugin = BasePlugin()
    assert plugin.should_handle_timeframe() is True
    settings.trading_control = not settings.trading_control
    assert plugin.should_handle_timeframe() is False
