import pytest
import asyncio
from unittest.mock import AsyncMock
from tt.config import settings
from tt.plugins.plugin_manager import PluginManager
from tt.plugins.message_processor import MessageProcessor
from tt.plugins.default_plugins.example_plugin import ExamplePlugin

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="message_processor")
def message_processor_fixture():
    plugin_manager = PluginManager()
    message_processor = MessageProcessor(plugin_manager)
    message_processor.load_plugins()
    return message_processor


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return ExamplePlugin()


@pytest.mark.asyncio
async def test_load_plugins(message_processor):
    loop = asyncio.get_running_loop()
    loop.create_task(message_processor.start_all_plugins())
    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_plugin(plugin, message_processor):
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    assert plugin.should_handle("any message") is True


@pytest.mark.asyncio
async def test_plugin_notification(plugin, message_processor):
    """Test notification """
    send_notification = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    send_notification.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_scheduling(plugin, message_processor):
    """Test scheduling """
    schedule_manager = AsyncMock()
    schedule_manager.schedule_example_hourly = AsyncMock()
    schedule_manager.schedule_example_every_8_hours = AsyncMock()
    assert settings.example_plugin_schedule_enabled is True
    schedule_manager.assert_awaited_once
    schedule_manager.schedule_example_hourly.assert_awaited_once
    schedule_manager.schedule_example_every_8_hours.assert_awaited_once