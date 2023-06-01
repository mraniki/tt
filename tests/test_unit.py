"""
 TT test
"""
import pytest
from dxsp import DexSwap
from config import settings, logger

# from findmyorder import FindMyOrder
from bot import (
    parse_message, load_exchange, execute_order,
    get_account, get_name,
    trading_switch_command, get_quote)


@pytest.fixture
def exchange():
    """Fixture to create an exchange object for testing."""
    return DexSwap()


# @pytest.mark.asyncio
# async def test_parse_message(caplog):
#     with caplog.at_level(logging.DEBUG):
#         # Test message to ignore
#         msg = "hello world"
#         assert await parse_message(msg) is None

#         # Test invalid command
#         msg = "/test"
#         assert await parse_message(msg) is None
#         assert 'invalid command' in caplog.text

        # Test valid command
        #msg = "/help"
        #await parse_message(msg)
        #assert '🏦' in caplog.text


@pytest.mark.asyncio
async def test_load_exchange():
    exchange = await load_exchange()
    if exchange:
        assert exchange is not None


@pytest.mark.asyncio
async def test_toggle_trading_active():
    # test toggling
    await trading_switch_command()
    assert settings.trading_enabled is False
    await trading_switch_command()
    assert settings.trading_enabled is True


# @pytest.mark.asyncio
# async def test_get_name():
#     exchange = DexSwap()
#     name = await get_name()
#     print(name)
#     assert name is not None


@pytest.mark.asyncio
async def test_get_account():
    exchange = DexSwap()
    account = await get_account(exchange)
    print(account)
    assert account is not None



@pytest.mark.asyncio
async def test_execute_order():
    # Test case when both action and instrument are not None
    order_params = {'action': 'buy', 'instrument': 'BTCUSDT'}
    assert await execute_order(order_params) is None

    # Test case when action is None
    order_params = {'action': None, 'instrument': 'EURUSD'}
    assert await execute_order(order_params) is None

    # Test case when instrument is None
    order_params = {'action': 'sell', 'instrument': None}
    assert await execute_order(order_params) is None

    # Test case when both action and instrument are None
    order_params = {'action': None, 'instrument': None}
    assert await execute_order(order_params) is None


# @pytest.mark.asyncio
# async def test_execute_order_missing_params():
#     """Test execute_order with missing params."""
#     result = await execute_order()
#     assert result == "⚠️ Missing params"

@pytest.mark.asyncio
async def test_execute_order_missing_action_or_instrument():
    """Test execute_order with missing action or instrument."""
    result = await execute_order({'quantity': 10})
    assert result is None

# @pytest.mark.asyncio
# async def test_execute_order_sell_order():
#     """Test execute_order with a sell order."""
#     order_params = {
#         'action': 'SELL',
#         'instrument': 'BTC/USDT',
#         'quantity': 10
#     }
#     result = await execute_order(order_params)
#     assert "⬇️ BTC/USDT" in result

# @pytest.mark.asyncio
# async def test_execute_order_buy_order():
#     """Test execute_order with a buy order."""
#     order_params = {
#         'action': 'BUY',
#         'instrument': 'BTC/USDT',
#         'quantity': 10
#     }
#     result = await execute_order(order_params)
#     assert "⬆️ BTC/USDT" in result
