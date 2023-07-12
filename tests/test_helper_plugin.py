import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from tt.utils import MessageProcessor, start_plugins
from tt.config import settings
from tt.plugins.helper_plugin import HelperPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    return HelperPlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling """
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    assert plugin.should_handle("any message") is True


@pytest.mark.asyncio
async def test_plugin_notification(plugin):
    """Test notification """
    plugin.send_notification = AsyncMock()
    with patch('plugins.example_plugin.send_notification'):
        await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
        plugin.send_notification.assert_called_once
    

@pytest.mark.asyncio
async def test_trading_switch(plugin):
    """Test switch """
    plugin.trading_switch_command = AsyncMock()
    with patch('plugins.example_plugin.send_notification'):
        await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_trading}")
        plugin.trading_switch_command.assert_called_once
        assert settings.trading_enabled is False

# @pytest.mark.asyncio
# async def test_help(message_processor, caplog):
#     plugin = HelperPlugin()
#     await plugin.handle_message('/help')
#     assert "🎯" in caplog.text
