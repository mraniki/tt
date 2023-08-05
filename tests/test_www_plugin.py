from unittest.mock import AsyncMock

import pytest

from tt.config import settings
from tt.plugins.default_plugins.www_plugin import WwwPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return WwwPlugin()


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
async def test_bot_ignore(plugin):
    msg = "⚠️"
    result =  await plugin.handle_message(msg)
    assert result is None


@pytest.mark.asyncio
async def test_parsing_help(plugin):
    """Test help """
    plugin.get_www_help = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_help}")
    plugin.get_www_help.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_info(plugin):
    """Test info """
    plugin.get_www_info = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_info}")
    plugin.get_www_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_scr(plugin):
    """Test scr """
    plugin.get_www_run = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_screenshot}")
    plugin.get_www_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_help(plugin):
    """Test help """
    result = await plugin.get_www_help() 
    assert result is not None


@pytest.mark.asyncio
async def test_info(plugin):
    """Test info """
    result = await plugin.get_www_info() 
    assert result is not None


# @pytest.mark.asyncio
# async def test_screenshot(plugin):
#     """Test screenshot """
#     result = await plugin.get_www_run()
#     assert result is not None
