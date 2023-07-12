import pytest
import asyncio
from unittest.mock import AsyncMock
from tt.utils import MessageProcessor, start_plugins
from tt.config import settings
from tt.plugins.example_plugin import ExamplePlugin



@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="message_processor")
def message_processor_fixture():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    return message_processor


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return ExamplePlugin()


@pytest.mark.asyncio
async def test_load_plugins(message_processor):
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_plugin(plugin, message_processor):
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    assert plugin.should_handle("any message") is True


@pytest.mark.asyncio
async def test_plugin_notification(plugin, message_processor):
    """Test notification """
    send_notification = AsyncMock()
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    send_notification.assert_called_once


@pytest.mark.asyncio
async def test_plugin_scheduling(plugin, message_processor):
    """Test scheduling """
    schedule_notifications = AsyncMock()
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    assert settings.example_plugin_schedule_enabled is True
    schedule_notifications.assert_called_once
