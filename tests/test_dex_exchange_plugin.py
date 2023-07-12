import pytest
from unittest.mock import AsyncMock
from dxsp import DexSwap
import iamlistening
from findmyorder import FindMyOrder
from iamlistening import Listener
from tt.config import settings
from tt.plugins.dex_exchange_plugin import DexExchangePlugin


@pytest.fixture(name="bsc")
def set_test_settings_DEX56():
    settings.configure(FORCE_ENV_FOR_DYNACONF="bsc")


@pytest.fixture(name="order")
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.fixture
def order():
    """return valid order"""
    return "buy WBTC sl=200 tp=400 q=1%"

@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return DexExchangePlugin()


def test_dynaconf_is_in_testing_env_DEX56(bsc):
    print(settings.VALUE)
    assert settings.VALUE == "On Testing DEX_56"
    assert settings.cex_name == ""
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234567899"


@pytest.mark.asyncio
async def test_listener_discord(bsc):
    print(settings.VALUE)
    listener_test = Listener()
    print(listener_test)
    assert listener_test is not None
    assert isinstance(listener_test, iamlistening.main.Listener)


@pytest.mark.asyncio
async def test_plugin(plugin):
    enabled = plugin.enabled
    fmo = plugin.fmo
    exchange = plugin.exchange
    print(exchange.account)
    assert enabled is True
    assert isinstance(fmo, FindMyOrder)
    assert isinstance(exchange, DexSwap)
    assert exchange.account is not None


@pytest.mark.asyncio
async def test_parse_valid_order(plugin, crypto_order):
    """Search Testing"""
    await plugin.handle_message(crypto_order)
    plugin.fmo.search.assert_called_once
    plugin.fmo.get_order.assert_called_once
    plugin.exchange.execute_order.assert_called_once


@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message balance """
    # enabled = plugin.enabled
    # exchange = plugin.exchange
    await plugin.handle_message('/q WBTC')
    assert "🦄" in caplog.text


@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance """
    # get_account_balance = AsyncMock()
    await plugin.handle_message('/bal')
    plugin.exchange.get_account_balance.assert_called_once


@pytest.mark.asyncio
async def test_parse_position(plugin):
    """Test balance """
    # get_account_position = AsyncMock()
    await plugin.handle_message('/pos')
    plugin.exchange.get_account_position.assert_called_once


@pytest.mark.asyncio
async def test_parse_pnl(plugin):
    """Test balance """
    # get_account_position = AsyncMock()
    await plugin.handle_message('/d')
    plugin.exchange.get_account_pnl.assert_called_once


@pytest.mark.asyncio
async def test_parse_help(plugin):
    """Test balance """
    # get_info = AsyncMock()
    await plugin.handle_message('/help')
    plugin.get_info.assert_called_once
