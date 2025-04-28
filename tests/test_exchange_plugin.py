import os
from unittest.mock import AsyncMock
import pytest
import importlib
from cefi import CexTrader
from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings as tt_settings
from tt.plugins.default_plugins.exchange_plugin import UnifiedExchangePlugin

# Try to import the module for reloading
try:
    import findmyorder.main as findmyorder_main
except ImportError:
    findmyorder_main = None
    print(
        "Warning: Could not import findmyorder.main for reloading "
        "in test_exchange_plugin."
    )


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_exchange():
    print(
        "\nConfiguring settings for [testing] environment "
        "in test_exchange_plugin.py..."
    )
    common_config = {
        "FORCE_ENV_FOR_DYNACONF": "testing",
        "ENVVAR_PREFIX_FOR_DYNACONF": "TT"
    }
    print("Configuring tt_settings...")
    tt_settings.configure(**common_config)
    tt_settings.reload()
    # Optional: Verify keys (using tt_settings)
    print(
        f"tt_settings exists('findmyorder_enabled')? "
        f"{tt_settings.exists('findmyorder_enabled')}"
    )
    print(
        f"tt_settings exists('cex_enabled')? "
        f"{tt_settings.exists('cex_enabled')}"
    )
    print(
        f"tt_settings exists('dxsp_enabled')? "
        f"{tt_settings.exists('dxsp_enabled')}"
    )
    print(
        f"tt_settings.findmyorder exists after reload? "
        f"{tt_settings.exists('findmyorder')}"
    )
    # Reload the dependent library module
    if findmyorder_main:
        try:
            importlib.reload(findmyorder_main)
            print("Reloaded findmyorder.main")
        except Exception as e:
            print(f"ERROR: Failed to reload findmyorder.main: {e}")
    else:
        print("Skipping reload for findmyorder.main (not imported).")

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
