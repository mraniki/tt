import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dxsp import DexSwap
from tt.config import settings, logger
from tt.plugins.dex_exchange_plugin import DexExchangePlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture(name="order")
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return DexExchangePlugin()

@pytest.mark.asyncio
async def test_plugin(plugin):
    enabled = plugin.enabled
    exchange = plugin.exchange
    assert enabled is True
    assert isinstance(exchange, DexSwap)

@pytest.mark.asyncio
async def test_parse_quote(plugin, caplog):
    """Test parse_message balance """
    #get_quote= AsyncMock("WBTC")
    enabled = plugin.enabled
    exchange = plugin.exchange
    await plugin.handle_message('/q WBTC')
    assert "🦄" in caplog.text

@pytest.mark.asyncio
async def test_parse_balance(plugin):
    """Test balance """
    get_account_balance= AsyncMock()
    await plugin.handle_message('/bal')
    get_account_balance.assert_called_once

@pytest.mark.asyncio
async def test_parse_position(plugin):
    """Test balance """
    get_account_position= AsyncMock()
    await plugin.handle_message('/pos')
    get_account_position.assert_called_once

@pytest.mark.asyncio
async def test_info_message(plugin):
    """test exchange dex"""
    output = await plugin.info_message()
    assert output is not None 

# @pytest.mark.asyncio
# async def test_execute_order(plugin, caplog, order):
#     execute_mock = AsyncMock()
#     with patch('tt.plugins.dex_exchange_plugin.execute_order',execute_mock):
#         trade_confirmation = await dex.execute_order(order)
#         assert "⚠️ order execution:" in caplog.text

# @pytest.mark.asyncio
# async def test_failed_execute_order(plugin, caplog, order):
#     output = await plugin.execute_order(order)
#     assert "⚠️" in caplog.text


@pytest.mark.asyncio
async def test_get_account_balance(plugin):
    """Test get_account_balance."""
    output = await plugin.get_account_balance()
    print(output)
    assert output is not None

@pytest.mark.asyncio
async def test_get_account_position(plugin):
    """Test get_account_positions."""
    output = await plugin.get_account_position()
    print(output)
    assert output is not None

@pytest.mark.asyncio
async def test_get_trading_asset_balance(plugin):
    """Test get_asset_trading_balance."""
    output = await plugin.get_trading_asset_balance()
    print(output)
    assert output is not None
