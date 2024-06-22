from unittest.mock import AsyncMock

import pytest

from tt.config import settings
from tt.plugins.default_plugins.talkytrend_plugin import TalkyTrendPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return TalkyTrendPlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling"""
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_help}")
    assert callable(plugin.plugin_notify_cron_task)


@pytest.mark.asyncio
async def test_plugin_notification(plugin):
    """Test notification"""
    plugin.send_notification = AsyncMock()
    plugin.get_talkytrend_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_help}")
    plugin.send_notification.assert_awaited_once
    plugin.get_talkytrend_info.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_info(plugin):
    """Test notification"""
    plugin.get_talkytrend_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_info}")
    plugin.get_talkytrend_info.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_tv(plugin):
    """Test notification"""
    plugin.get_tv = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_tv}")
    plugin.get_tv.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_trend(plugin):
    """Test notification"""
    plugin.fetch_signal = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_trend}")
    plugin.fetch_signal.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_news(plugin):
    """Test notification"""
    plugin.fetch_feed = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_news}")
    plugin.fetch_feed.assert_awaited_once
