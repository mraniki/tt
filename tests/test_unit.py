"""
 TT test
"""
import pytest
import logging
from dxsp import DexSwap
# from findmyorder import FindMyOrder
from bot import parse_message, load_exchange, execute_order


@pytest.fixture
def exchange():
    """Fixture to create an exchange object for testing."""
    return DexSwap()


@pytest.mark.asyncio
async def test_parse_message(caplog):
    with caplog.at_level(logging.DEBUG):
        # Test message to ignore
        msg = "hello world"
        assert await parse_message(msg) is None

        # Test invalid command
        msg = "/test"
        assert await parse_message(msg) is None
        assert 'invalid command' in caplog.text

        # Test valid command
        msg = "/help"
        await parse_message(msg)
        assert '🏦' in caplog.text


@pytest.mark.asyncio
async def test_load_exchange():
    exchange = await load_exchange()
    if exchange:
        assert exchange is not None


# @pytest.mark.asyncio
# async def test_get_quote():
#     exchange = DexSwap()
#     symbol = "WBTC"
#     quote = await get_quote(symbol)
#     print(quote)
#     assert quote is not None


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
