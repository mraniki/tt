from unittest.mock import AsyncMock

import pytest
from dxsp import DexSwap
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.default_plugins.dex_exchange_plugin import DexExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="order_message")
def order():
    """return valid order"""
    return "buy WBTC sl=200 tp=400 q=1%"


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return DexExchangePlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    enabled = plugin.enabled
    fmo = plugin.fmo
    exchange = plugin.exchange
   # assert enabled is True
    assert isinstance(fmo, FindMyOrder)
    assert isinstance(exchange, DexSwap)
    assert exchange.account is not None


@pytest.mark.asyncio
async def test_parse_valid_order(plugin, order_message):
    """Search Testing"""
    plugin.fmo.search = AsyncMock()
    plugin.fmo.get_order = AsyncMock()
    plugin.exchange.execute_order = AsyncMock()
    await plugin.handle_message(order_message)
    plugin.fmo.search.assert_awaited_once
    plugin.fmo.get_order.assert_awaited
    plugin.exchange.execute_order.assert_awaited


@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message balance"""
    plugin.exchange.get_quote = AsyncMock()
    await plugin.handle_message("/q WBTC")
    plugin.exchange.get_quote.assert_awaited


@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance"""
    plugin.exchange.get_account_balance = AsyncMock()
    await plugin.handle_message("/bal")
    plugin.exchange.get_account_balance.assert_awaited


@pytest.mark.asyncio
async def test_parse_position(plugin):
    """Test position"""
    plugin.exchange.get_account_position = AsyncMock()
    await plugin.handle_message("/pos")
    plugin.exchange.get_account_position.assert_awaited


@pytest.mark.asyncio
async def test_parse_help(plugin):
    """Test help"""
    plugin.exchange.get_help = AsyncMock()
    await plugin.handle_message("/help")
    plugin.exchange.get_help.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_info(plugin):
    """Test help"""
    plugin.exchange.get_info = AsyncMock()
    await plugin.handle_message("/info")
    plugin.exchange.get_info.assert_awaited_once()
