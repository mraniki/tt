import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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

@pytest.fixture(name="wrong_order")
def wrong_order():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
        }

@pytest.fixture(name="dex")
@pytest.mark.asyncio
async def test_dex_exchange():
    # Arrange
    plugin = DexExchangePlugin()
    return plugin

@pytest.mark.asyncio
async def test_dex_exchange_plugin(dex):
    # Arrange
    assert dex is not None
    assert isinstance(dex, dxsp.DexSwap)
    # Act
    #await plugin.start()
    # await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    # await plugin.handle_message(f"{settings.bot_prefix}{settings.plugin_menu}")
    # await plugin.stop()
    # assert plugin.should_handle("any message") is True

@pytest.mark.asyncio
async def test_dex_quote(dex, caplog):
    """Test parse_message balance """
    #get_quote= AsyncMock("WBTC")
    await dex.handle_message('/q WBTC')
    assert 'quote [1, 0]' in caplog.text

@pytest.mark.asyncio
async def test_dex_balance(dex):
    """Test balance """
    #send_notification_mock = AsyncMock()
    get_account_balance= AsyncMock()
    await dex.handle_message('/bal')
    get_account_balance.assert_called_once

@pytest.mark.asyncio
async def test_dex_position(dex):
    """Test balance """
    get_account_position= AsyncMock()
    await dex.handle_message('/pos')
    get_account_position.assert_called_once

@pytest.mark.asyncio
async def test_dex_load_exchange(dex):
    """test exchange dex"""
    account = await dex.get_account()
    assert account == "1 - 34567890"

@pytest.mark.asyncio
async def test_failure_execute_order(dex, caplog, order):
    execute_mock = AsyncMock()
    with patch('tt.plugins.dex_exchange_plugin.execute_order',execute_mock):
        trade_confirmation = await dex.execute_order(order)
        assert "⚠️ order execution:" in caplog.text






# @pytest.mark.asyncio
# async def test_failed_execute_order(caplog, order):
#     await load_exchange()
#     trade_confirmation = await execute_order(order)
#     assert "🗓️" not in caplog.text


# @pytest.mark.asyncio
# async def test_get_quote():
#     """Test get_quote """
#     await load_exchange()
#     output = await get_quote("WBTC")
#     print(output)
#     assert output is not None


# @pytest.mark.asyncio
# async def test_get_account_balance():
#     """Test get_account_balance."""
#     await load_exchange()
#     output = await get_account_balance()
#     print(output)
#     assert output is not None


# @pytest.mark.asyncio
# async def test_get_trading_asset_balance():
#     """Test get_asset_trading_balance."""
#     await load_exchange()
#     output = await get_trading_asset_balance()
#     print(output)
#     assert output is not None

    
# @pytest.mark.asyncio
# async def test_get_account_position():
#     """Test get_account_positions."""
#     await load_exchange() 
#     output = await get_account_position()
#     print(output)
#     assert output is not None


# @pytest.mark.asyncio
# async def test_get_account_margin():
#     """Test get_account_margin """
#     await load_exchange() 
#     output = await get_account_margin()
#     print(output)
#     assert output is not None

# @pytest.mark.asyncio
# async def test_parse_command_plugin(mock_settings_dex):
#     """Test parse_message balance """
#     send_notification_mock = AsyncMock()
#     with patch('tt.utils.send_notification',send_notification_mock):
#         message_processor = MessageProcessor()
#     # if settings.plugin_enabled:
#         message_processor.load_plugins("tt.plugins")
#         loop = asyncio.get_running_loop()
#         await loop.create_task(start_plugins(message_processor))
#         await message_processor.process_message('/plugin')
#         assert '⚙️' in send_notification_mock.call_args[0][0]


# @pytest.fixture
# async def test_listener(plugin_enabled):
#     bot_listener = Listener()
#     task = asyncio.create_task(bot_listener.run_forever())
#     message_processor = MessageProcessor()
#     if settings.plugin_enabled:
#         message_processor.load_plugins("tt.plugins")
#         loop = asyncio.get_running_loop()
#         loop.create_task(start_plugins(message_processor))
#     task = asyncio.create_task(bot_listener.run_forever())

#     yield bot_listener

#     await bot_listener.stop()
#     task.cancel()

# @pytest.fixture
# def message_processor():
#     return MessageProcessor()