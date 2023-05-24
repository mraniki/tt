"""
 TT test
"""
import pytest
from bot import parse_message, load_exchange, execute_order


@pytest.mark.asyncio
async def test_parse_message():
    # Test invalid command
    msg = "!foo"
    assert await parse_message(msg) is None

    # Test message to ignore
    msg = "hello world"
    assert await parse_message(msg) is None


@pytest.mark.asyncio
async def test_load_exchange():
    exchange = await load_exchange()
    if exchange:
        assert exchange is not None

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