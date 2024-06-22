from unittest.mock import AsyncMock

import pytest

from tt.config import settings
from tt.plugins.default_plugins.helper_plugin import HelperPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return HelperPlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling"""
    assert plugin.should_filter("ℹ️") is True
    assert (
        plugin.should_filter(f"{plugin.bot_prefix}{plugin.bot_command_help}")
        is False
    )
    assert (
        plugin.should_handle(f"{plugin.bot_prefix}{plugin.bot_command_help}")
        is True
    )
    assert (
        plugin.is_command_to_handle(f"{plugin.bot_prefix}{plugin.bot_command_help}")
        is True
    )


@pytest.mark.asyncio
async def test_plugin_notification(plugin):
    """Test notification"""
    plugin.send_notification = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_help}")
    plugin.send_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_bot_ignore(plugin):
    msg = "⚠️"
    result = await plugin.handle_message(msg)
    assert result is None


@pytest.mark.asyncio
async def test_parsing_help(plugin):
    """Test help"""
    plugin.get_helper_help = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_help}")
    plugin.get_helper_help.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_info(plugin):
    """Test info"""
    plugin.get_helper_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_info}")
    plugin.get_helper_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_network(plugin):
    """Test network"""
    plugin.get_helper_network = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_network}")
    plugin.get_helper_network.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_trading_switch(plugin):
    """Test switch"""
    plugin.trading_switch_command = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_trading}")
    plugin.trading_switch_command.assert_awaited_once()


@pytest.mark.asyncio
async def test_help(plugin):
    """Test help"""
    result = await plugin.get_helper_help()
    assert result is not None


@pytest.mark.asyncio
async def test_info(plugin):
    """Test help"""
    result = await plugin.get_helper_info()
    assert result is not None


@pytest.mark.asyncio
async def test_network(plugin):
    """Test help"""
    result = await plugin.get_helper_network()
    assert result is not None


@pytest.mark.asyncio
async def test_trading_switch(plugin):
    """Test help"""
    result = await plugin.trading_switch_command()
    assert result is not None
    assert "Trading" in result
    assert plugin.trading_enabled is False
