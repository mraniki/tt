import pytest
from unittest.mock import AsyncMock
from tt.config import settings
from tt.plugins.default_plugins.helper_plugin.helper_plugin import HelperPlugin


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
    plugin.send_notification.assert_awaited_once()
    

@pytest.mark.asyncio
async def test_trading_switch(plugin):
    """Test switch """
    plugin.trading_switch_command = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_trading}")
    plugin.trading_switch_command.assert_awaited_once()



@pytest.mark.asyncio
async def test_help(plugin,caplog):
    """Test switch """
    plugin.get_helper_info = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_help}")
    print(caplog.text)
    plugin.get_helper_info.assert_awaited_once()