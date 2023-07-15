import pytest
from unittest.mock import AsyncMock
from tt.config import settings
from tt.plugins.talkytrend_plugin import TalkyTrendPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return TalkyTrendPlugin()


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
    plugin.send_notification.assert_awaited_once

@pytest.mark.asyncio
async def test_plugin_tv(plugin):
    """Test notification """
    plugin.send_notification = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_news}")
    plugin.send_notification.assert_awaited_once

# @pytest.mark.asyncio
# async def test_news(plugin):
#     """Test switch """
#     plugin.send_notification = AsyncMock()
#     await plugin.handle_message(
#         f"{settings.bot_prefix}{settings.settings.bot_command_news}")
#     plugin.send_notification.assert_called_once
