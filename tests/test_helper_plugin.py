import pytest
from unittest.mock import AsyncMock
from tt.config import settings
from tt.plugins.helper_plugin import HelperPlugin



@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
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
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    plugin.send_notification.assert_called_once
    

@pytest.mark.asyncio
async def test_trading_switch(plugin):
    """Test switch """
    plugin.trading_switch_command = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_trading}")
    plugin.trading_switch_command.assert_called_once



@pytest.mark.asyncio
async def test_help(plugin):
    """Test switch """
    plugin.get_info = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_help}")
    plugin.get_info.assert_called_once()