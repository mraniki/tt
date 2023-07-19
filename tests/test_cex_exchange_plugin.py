from unittest.mock import AsyncMock

import ccxt
import pytest
from ccxt.base.errors import AuthenticationError

from tt.config import settings
from tt.plugins.default_plugins.cex_exchange_plugin import CexExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="cex")


@pytest.fixture(name="order_message")
def order():
    """return valid order"""
    return "buy BTCUSDT sl=200 tp=400 q=1%"


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return CexExchangePlugin()


def test_dynaconf_is_in_testing_env_CEX():
    print(settings.VALUE)
    assert settings.VALUE == "On Testing CEX_binance"
    assert settings.cex_name == "binance"
    assert settings.cex_api == 'api_key'


@pytest.mark.asyncio
async def test_plugin(plugin):
    enabled = plugin.enabled
    exchange = plugin.exchange
    assert enabled is True
    assert isinstance(exchange, ccxt.binance)


@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message balance """
    exchange = plugin.exchange
    print(exchange.id)
    await plugin.handle_message('/q BTCUSDT')
    assert "🏦" in caplog.text


@pytest.mark.asyncio
async def test_info_message(plugin):
    """test exchange cex"""
    output = await plugin.get_info()
    assert output is not None


@pytest.mark.asyncio
async def test_parse_valid_order(plugin, order_message):
    """Search Testing"""
    plugin.fmo.search = AsyncMock()
    plugin.fmo.get_order = AsyncMock()
    plugin.exchange.execute_order = AsyncMock()
    await plugin.handle_message(order_message)
    plugin.fmo.search.assert_awaited_once
    plugin.fmo.get_order.assert_awaited_once
    plugin.exchange.execute_order.assert_awaited_once


@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance """
    with pytest.raises(AuthenticationError):
        plugin.exchange.assert_awaited_once = AsyncMock()
        await plugin.handle_message('/bal')
        # plugin.exchange.get_account_balance.assert_called()


@pytest.mark.asyncio
async def test_parse_position(plugin, caplog):
    """Test position """
    with pytest.raises(AuthenticationError):
        plugin.exchange.get_account_position = AsyncMock()
        await plugin.handle_message('/pos')
        assert "API-key format invalid" in caplog
        # plugin.exchange.get_account_position.assert_called()


@pytest.mark.asyncio
async def test_get_account_pnl(plugin):
    """Test pnl """
    plugin.get_account_pnl = AsyncMock()
    await plugin.handle_message('/d')
    plugin.get_account_pnl.assert_awaited_once()