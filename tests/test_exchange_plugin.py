from unittest.mock import AsyncMock

import pytest
import os
from cefi import CexTrader
from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings as tt_settings
from findmyorder.config import settings as findmyorder_settings
import findmyorder.config as findmyorder_config_module
from cefi.config import settings as cefi_settings
import cefi.config as cefi_config_module
from dxsp.config import settings as dxsp_settings
import dxsp.config as dxsp_config_module

from tt.plugins.default_plugins.exchange_plugin import UnifiedExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_exchange():
    print("\nConfiguring settings for [testing] environment in test_exchange_plugin.py...")

    # --- Determine Paths ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tt_root = os.path.dirname(current_dir)
    settings_path = os.path.join(tt_root, 'settings.toml')
    talky_settings_path = os.path.join(tt_root, 'tt', 'talky_settings.toml')
    # Lib default paths (assuming standard structure)
    findmyorder_default_path = os.path.join(os.path.dirname(findmyorder_config_module.__file__), 'default_settings.toml')
    cefi_default_path = os.path.join(os.path.dirname(cefi_config_module.__file__), 'default_settings.toml')
    dxsp_default_path = os.path.join(os.path.dirname(dxsp_config_module.__file__), 'default_settings.toml')

    print(f"Located tt settings.toml at: {settings_path}")
    print(f"Located tt talky_settings.toml at: {talky_settings_path}")

    # --- Determine Files to Load ---
    files_to_load_tt = []
    if os.path.exists(talky_settings_path): files_to_load_tt.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_tt.append(settings_path)

    # Lib files (adjust based on actual loading logic if needed)
    files_to_load_findmyorder = []
    if os.path.exists(findmyorder_default_path): files_to_load_findmyorder.append(findmyorder_default_path)
    if os.path.exists(talky_settings_path): files_to_load_findmyorder.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_findmyorder.append(settings_path)

    files_to_load_cefi = []
    if os.path.exists(cefi_default_path): files_to_load_cefi.append(cefi_default_path)
    if os.path.exists(talky_settings_path): files_to_load_cefi.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_cefi.append(settings_path)

    files_to_load_dxsp = []
    if os.path.exists(dxsp_default_path): files_to_load_dxsp.append(dxsp_default_path)
    if os.path.exists(talky_settings_path): files_to_load_dxsp.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_dxsp.append(settings_path)

    # --- Configure Settings Objects ---
    common_config = {
        "FORCE_ENV_FOR_DYNACONF": "testing",
        "ENVVAR_PREFIX_FOR_DYNACONF": "TT"
    }

    print(f"Configuring tt_settings with files: {files_to_load_tt}")
    tt_settings.configure(**common_config, SETTINGS_FILE_FOR_DYNACONF=files_to_load_tt)

    print(f"Configuring findmyorder_settings with files: {files_to_load_findmyorder}")
    findmyorder_settings.configure(**common_config, SETTINGS_FILE_FOR_DYNACONF=files_to_load_findmyorder)

    print(f"Configuring cefi_settings with files: {files_to_load_cefi}")
    cefi_settings.configure(**common_config, SETTINGS_FILE_FOR_DYNACONF=files_to_load_cefi)

    print(f"Configuring dxsp_settings with files: {files_to_load_dxsp}")
    dxsp_settings.configure(**common_config, SETTINGS_FILE_FOR_DYNACONF=files_to_load_dxsp)

    # Optional: Verify keys
    print(f"findmyorder_settings exists('findmyorder_enabled')? {findmyorder_settings.exists('findmyorder_enabled')}")
    print(f"findmyorder value: {findmyorder_settings.get('findmyorder_enabled')}")
    print(f"cefi_settings exists('cex_enabled')? {cefi_settings.exists('cex_enabled')}")
    print(f"cefi value: {cefi_settings.get('cex_enabled')}")
    print(f"dxsp_settings exists('dxsp_enabled')? {dxsp_settings.exists('dxsp_enabled')}")
    print(f"dxsp value: {dxsp_settings.get('dxsp_enabled')}")

    print("Settings configuration complete in test_exchange_plugin.py.")


@pytest.fixture(name="order_message")
def order():
    """return valid order"""
    return "buy WBTC sl=200 tp=400 q=1%"


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return UnifiedExchangePlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    fmo = plugin.fmo
    exchange_dex = plugin.exchange_dex
    exchange_cex = plugin.exchange_cex
    assert isinstance(fmo, FindMyOrder)
    assert isinstance(exchange_dex, DexSwap)
    assert isinstance(exchange_cex, CexTrader)


@pytest.mark.asyncio
async def test_parse_info(plugin):
    """Test help"""
    plugin.get_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_info}")
    plugin.get_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance"""
    plugin.get_balances = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_bal}")
    plugin.get_balances.assert_awaited


@pytest.mark.asyncio
async def test_parse_position(plugin):
    """Test position"""
    plugin.get_positions = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_pos}")
    plugin.get_positions.assert_awaited


@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message quote"""
    plugin.get_quotes = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_quote} WBTC")
    plugin.get_quotes.assert_awaited


@pytest.mark.asyncio
async def test_parse_quote2(plugin, caplog):
    """Test parse_message quote 2"""
    plugin.get_quotes = AsyncMock()
    await plugin.handle_message(
        f"{plugin.bot_prefix}{plugin.bot_command_quote} BTCUSDT"
    )
    plugin.get_quotes.assert_awaited()


@pytest.mark.asyncio
async def test_parse_valid_order(plugin, order_message):
    """Search Testing"""
    plugin.fmo.search = AsyncMock()
    plugin.fmo.get_order = AsyncMock()
    plugin.submit_order = AsyncMock()
    await plugin.handle_message(order_message)
    plugin.fmo.search.assert_awaited_once
    plugin.fmo.get_order.assert_awaited
    plugin.submit_order.assert_awaited


@pytest.mark.asyncio
async def test_parse_ignore(plugin):
    """Search Testing"""
    result = await plugin.handle_message("🏦 balance")
    assert result is None
    assert plugin.should_filter("🏦 balance") is True


@pytest.mark.asyncio
async def test_info(plugin):
    """Search Testing"""
    results = await plugin.get_info()
    assert results is not None


@pytest.mark.asyncio
async def test_balance(plugin):
    """Search Testing"""
    results = await plugin.get_balances()
    assert results is not None


@pytest.mark.asyncio
async def test_position(plugin):
    """Search Testing"""
    results = await plugin.get_positions()
    assert results is not None


@pytest.mark.asyncio
async def test_quote(plugin, order_message):
    """Search Testing"""
    results = await plugin.get_quotes("WBTC")
    assert results is not None


@pytest.mark.asyncio
async def test_submit_order(plugin, order_message):
    """Search Testing"""
    results = await plugin.submit_order(order_message)
    assert results is not None
