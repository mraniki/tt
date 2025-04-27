import os  # Import os
from unittest.mock import AsyncMock

import pytest
# import talkytrend.config as talkytrend_config_module # REMOVED

# Import & Alias Lib settings
# from talkytrend.config import settings as talkytrend_settings # REMOVED

from tt.config import settings as tt_settings
from tt.plugins.default_plugins.talkytrend_plugin import TalkyTrendPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_talkytrend(): # Renamed for clarity
    print(
        "\nConfiguring settings for [testing] environment "
        "in test_talkytrend_plugin.py..."
    )

    # --- REMOVED PATH AND FILE LOADING LOGIC --- 

    # --- Configure Settings Objects ---
    common_config = {
        "FORCE_ENV_FOR_DYNACONF": "testing",
        "ENVVAR_PREFIX_FOR_DYNACONF": "TT"
    }

    print("Configuring tt_settings...") # Simplified print
    tt_settings.configure(**common_config) # Simplified configure

    # --- REMOVED talkytrend_settings.configure() --- 

    # Optional: Verify keys (using tt_settings)
    print(
        f"tt_settings exists('talkytrend_enabled')? "
        f"{tt_settings.exists('talkytrend_enabled')}"
    )

    print("Settings configuration complete in test_talkytrend_plugin.py.")


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
    plugin.get_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_help}")
    plugin.send_notification.assert_awaited_once
    plugin.get_info.assert_awaited_once


@pytest.mark.asyncio
async def test_plugin_info(plugin):
    """Test notification"""
    plugin.get_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_info}")
    plugin.get_info.assert_awaited_once

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

@pytest.mark.asyncio
async def test_plugin_tv(plugin):
    """Test notification"""
    plugin.fetch_tv = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_tv}")
    plugin.fetch_tv.assert_awaited_once

@pytest.mark.asyncio
async def test_plugin_fetch_page(plugin):
    """Test notification"""
    plugin.fetch_page = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_tv}")
    plugin.fetch_page.assert_awaited_once

