from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from findmyorder import FindMyOrder

from tt.config import settings
from tt.plugins.default_plugins.cex_exchange_plugin import CexExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="order_message")
def order():
    """return valid order"""
    return "buy BTCUSDT sl=200 tp=400 q=1%"


@pytest.fixture(name="order_parsed")
def result_order():
    """return standard expected results"""
    return {
        "action": "BUY",
        "instrument": "EURUSD",
        "stop_loss": 200,
        "take_profit": 400,
        "quantity": 2,
        "order_type": None,
        "leverage_type": None,
        "comment": None,
        "timestamp": datetime.now(),
    }


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return CexExchangePlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    enabled = plugin.enabled
    fmo = plugin.fmo
    assert enabled is True
    assert isinstance(fmo, FindMyOrder)


@pytest.mark.asyncio
async def test_parse_info(plugin):
    """Test info"""
    plugin.exchange.get_info = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_info}")
    plugin.exchange.get_info.assert_awaited()


@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance"""
    plugin.exchange.get_balances = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_bal}")
    plugin.exchange.get_balances.assert_awaited()


@pytest.mark.asyncio
async def test_parse_position(plugin):
    """Test position"""
    plugin.exchange.get_positions = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_pos}")
    plugin.exchange.get_positions.assert_awaited()


@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message balance"""
    plugin.exchange.get_quotes = AsyncMock()
    # await plugin.handle_message("/q BTCUSDT")
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_quote} BTCUSDT"
    )
    plugin.exchange.get_quotes.assert_awaited()


@pytest.mark.asyncio
async def test_parse_valid_order(plugin, order_message):
    """Search Testing"""
    plugin.fmo.search = AsyncMock()
    plugin.fmo.get_order = AsyncMock()
    plugin.exchange.submit_order = AsyncMock()
    await plugin.handle_message(order_message)
    plugin.fmo.search.assert_awaited_once
    plugin.fmo.get_order.assert_awaited_once
    plugin.exchange.submit_order.assert_awaited


@pytest.mark.asyncio
async def test_parse_ignore(plugin):
    """Search Testing"""
    result = await plugin.handle_message("🏦 balance")
    assert result is None
    assert plugin.should_filter("🏦 balance") is True
