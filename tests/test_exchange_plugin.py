from unittest.mock import AsyncMock

import pytest
from cefi import CexTrader
from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.default_plugins.exchange_plugin import UnifiedExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


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
